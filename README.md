# MacOS

For macOS versions **earlier than 11**, the system image needs to be created using:
[https://github.com/oneclickvirt/macos/blob/main/.github/workflows/build\_full\_iso.yml](https://github.com/oneclickvirt/macos/blob/main/.github/workflows/build_full_iso.yml)

For macOS versions **11 and later**, the system image should be created using:
[https://github.com/oneclickvirt/macos/blob/main/appveyor.yml](https://github.com/oneclickvirt/macos/blob/main/appveyor.yml)

If you need to edit and modify it by yourself, after you fork this repository, you need to set the IP and PASSWORD in the settings of the repository, or create a project in appveyor to track the repository after you fork it, and then add the IP and PASSWORD in the settings of the project, and then the image will be automatically uploaded to the /root/macos folder of the server with the corresponding IP after you execute the task. 

Note: The path to the server where the result file of the whole project task will be executed needs to be at least 120G hard disk, otherwise the upload will fail.

Thanks to:

* [https://github.com/corpnewt/gibMacOS](https://github.com/corpnewt/gibMacOS)
* [https://github.com/acidanthera/OpenCorePkg](https://github.com/acidanthera/OpenCorePkg)
