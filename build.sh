#!/bin/bash -e
export PATH="$PWD/build/venv/bin:$PWD/build/venv/Scripts:$PATH"
if [[ ! -d "$PWD/build/venv" ]]; then
  echo "virtualenv not ready"
  exit 1
fi

# Install the core packages.
pip install \
  'PyInstaller===4.3' \
  'beautifulsoup4===4.9.3' \
  'chardet===4.0.0'

# Build the binary.
python -OO -m PyInstaller \
  --noconfirm \
  --console \
  --onefile \
  --distpath build/dist \
  --specpath build \
  smi2ass.py

# Rename the binary.
OS_CLASSIFIER="$(./os_classifier.sh)"
if [[ -f build/dist/smi2ass.exe ]]; then
  SMI2ASS_BIN="build/dist/smi2ass.$OS_CLASSIFIER.exe"
  mv -v build/dist/smi2ass.exe "$SMI2ASS_BIN"
else
  SMI2ASS_BIN="build/dist/smi2ass.$OS_CLASSIFIER"
  mv -v build/dist/smi2ass "$SMI2ASS_BIN"
fi

# Generate the SHA256 checksum.
if [[ -x /usr/local/bin/gsha256sum ]]; then
  SHA256SUM_BIN=/usr/local/bin/gsha256sum
else
  SHA256SUM_BIN=sha256sum
fi
"$SHA256SUM_BIN" -b "$SMI2ASS_BIN" | sed 's/ .*//g' > "$SMI2ASS_BIN.sha256"
echo "sha256sum: $(cat "$SMI2ASS_BIN.sha256") ($SMI2ASS_BIN.sha256)"

# Build a test site with the binary to make sure it really works.
"build/dist/smi2ass.$OS_CLASSIFIER" 'test_smis/Psycho-Pass - S01E15.smi'
"build/dist/smi2ass.$OS_CLASSIFIER" 'test_smis/Bakemonogatari - 01.smi'
