wget --recursive --no-parent "https://buddhanexus.net/json/chn/"
mkdir data/chn/
find buddhanexus.net/json/chn/ -name "*json.gz" -exec cp "{}" data/chn \;
rm -rf buddhanexus.net
