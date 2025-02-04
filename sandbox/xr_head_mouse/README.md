1. add viture sdk into base directory (or symlink)
2. ``gcc viture-logger.c -I viture_one_linux_sdk_1.0.7/include/ -Lviture_one_linux_sdk_1.0.7/libs/ -l:libviture_one_sdk.so -L/nix/store/bzk3q2l71qwhycsip23y6rl5n881la4n-zlib-1.3.1/lib -lz -o build/viture-logger``
3. run the python script as ``LD_LIBRARY_PATH=`pwd`/viture_one_linux_sdk_1.0.7/libs python viture_xr_mouse.py``

OR

2. ``gcc viture-logger.c -I viture_one_linux_sdk_1.0.7/include/ -Lviture_one_linux_sdk_1.0.7/libs/ -l:libviture_one_sdk_static.a -L/nix/store/bzk3q2l71qwhycsip23y6rl5n881la4n-zlib-1.3.1/lib -lz -L/nix/store/lsadm835pyf0kvldk3ckhwahs16v1zfw-libusb-1.0.27/lib/ -lusb-1.0 -o build/viture-logger``
3. ``python viture_xr_mouse.py``