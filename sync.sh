#!/bin/bash
cd ..
rsync -avr --progress --exclude 'VirtEnv' --exclude api --exclude display photoboo pi@photoboo.local:~/
