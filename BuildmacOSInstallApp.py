#!/usr/bin/env python3
import os
import sys
import plistlib
import subprocess
import shutil

def run_command(cmd):
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    stdout, stderr = process.communicate()
    return stdout, stderr, process.returncode

def mount_dmg(dmg_path, no_browse=False):
    args = ["/usr/bin/hdiutil", "attach", dmg_path, "-plist", "-noverify"]
    if no_browse:
        args.append("-nobrowse")
    
    stdout, stderr, returncode = run_command(args)
    if returncode != 0:
        raise Exception(f"{os.path.basename(dmg_path)} failed to mount:\n{stderr}")
    
    try:
        with open('/tmp/mount_output.plist', 'w') as f:
            f.write(stdout)
        
        with open('/tmp/mount_output.plist', 'rb') as f:
            plist_data = plistlib.load(f)
        
        mounts = [x["mount-point"] for x in plist_data.get("system-entities", []) if "mount-point" in x]
        return mounts
    except Exception as e:
        raise Exception(f"No mount points returned from {os.path.basename(dmg_path)}: {str(e)}")

def unmount_dmg(mount_point):
    if not isinstance(mount_point, list):
        mount_point = [mount_point]
    
    unmounted = []
    for m in mount_point:
        args = ["/usr/bin/hdiutil", "detach", m]
        stdout, stderr, returncode = run_command(args)
        if returncode != 0:
            args.append("-force")
            stdout, stderr, returncode = run_command(args)
            if returncode != 0:
                print(stderr)
                continue
        unmounted.append(m)
    return unmounted

def build_installer(folder_path):
    target_files = [
        "BaseSystem.dmg",
        "BaseSystem.chunklist",
        "InstallESDDmg.pkg",
        "InstallInfo.plist",
        "AppleDiagnostics.dmg",
        "AppleDiagnostics.chunklist"
    ]
    
    # Check if all files exist
    for file in target_files:
        file_path = os.path.join(folder_path, file)
        if not os.path.exists(file_path):
            print(f"Missing required file: {file}")
            return False
    
    # Process starts here
    base_mounts = []
    try:
        print("Taking ownership of downloaded files...")
        for file in target_files:
            file_path = os.path.join(folder_path, file)
            print(f" - {file}...")
            run_command(["chmod", "a+x", file_path])
        
        print("Mounting BaseSystem.dmg...")
        base_system_path = os.path.join(folder_path, "BaseSystem.dmg")
        base_mounts = mount_dmg(base_system_path)
        
        if not base_mounts:
            raise Exception("No mount points were returned from BaseSystem.dmg")
        
        base_mount = base_mounts[0]
        print("Locating Installer app...")
        
        install_app = None
        for item in os.listdir(base_mount):
            item_path = os.path.join(base_mount, item)
            if (os.path.isdir(item_path) and 
                item.lower().endswith(".app") and 
                not item.startswith(".")):
                install_app = item
                break
        
        if not install_app:
            raise Exception(f"Installer app not located in {base_mount}")
        
        print(f" - Found {install_app}")
        
        # Copy the .app over
        source_app = os.path.join(base_mount, install_app)
        dest_app = os.path.join(folder_path, install_app)
        stdout, stderr, returncode = run_command(["cp", "-R", source_app, dest_app])
        
        if returncode != 0:
            raise Exception(f"Copy Failed! {stderr}")
        
        print("Unmounting BaseSystem.dmg...")
        for mount in base_mounts:
            unmount_dmg(mount)
        base_mounts = []
        
        shared_support = os.path.join(dest_app, "Contents", "SharedSupport")
        if not os.path.exists(shared_support):
            print("Creating SharedSupport directory...")
            os.makedirs(shared_support)
        
        print("Copying files to SharedSupport...")
        for file in target_files:
            source_file = os.path.join(folder_path, file)
            # InstallESDDmg.pkg gets renamed to InstallESD.dmg - all others stay the same
            dest_file_name = "InstallESD.dmg" if file.lower() == "installesddmg.pkg" else file
            dest_file = os.path.join(shared_support, dest_file_name)
            
            rename_msg = f" --> {dest_file_name}" if dest_file_name != file else ""
            print(f" - {file}{rename_msg}")
            
            stdout, stderr, returncode = run_command(["cp", "-R", source_file, dest_file])
            if returncode != 0:
                raise Exception(f"Copy Failed! {stderr}")
        
        print("Patching InstallInfo.plist...")
        plist_path = os.path.join(shared_support, "InstallInfo.plist")
        
        with open(plist_path, "rb") as f:
            p = plistlib.load(f)
        
        if "Payload Image Info" in p:
            pii = p["Payload Image Info"]
            if "URL" in pii:
                pii["URL"] = pii["URL"].replace("InstallESDDmg.pkg", "InstallESD.dmg")
            if "id" in pii:
                pii["id"] = pii["id"].replace("com.apple.pkg.InstallESDDmg", "com.apple.dmg.InstallESD")
            
            if "chunklistURL" in pii:
                del pii["chunklistURL"]
            if "chunklistid" in pii:
                del pii["chunklistid"]
        
        with open(plist_path, "wb") as f:
            plistlib.dump(p, f)
        
        print(f"\nCreated: {install_app}")
        print(f"Saved to: {dest_app}")
        return dest_app
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        
        if base_mounts:
            for mount in base_mounts:
                print(f" - Unmounting {mount}...")
                unmount_dmg(mount)
        
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 BuildmacOSInstallApp.py /path/to/downloaded/files")
        sys.exit(1)
    
    folder_path = sys.argv[1]
    if not os.path.isdir(folder_path):
        print(f"Error: {folder_path} is not a directory")
        sys.exit(1)
    
    output_path = sys.argv[2] if len(sys.argv) > 2 else folder_path
    if not os.path.isdir(output_path):
        os.makedirs(output_path)
    
    result = build_installer(folder_path)
    if result:
        app_name = os.path.basename(result)
        if output_path != folder_path:
            # Move the result to the output path if different
            shutil.move(result, os.path.join(output_path, app_name))
            print(f"Moved to: {os.path.join(output_path, app_name)}")
        sys.exit(0)
    else:
        sys.exit(1)
