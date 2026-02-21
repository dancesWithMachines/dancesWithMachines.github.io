---
layout: post
title: "Realtek rtl8852bu bluetooth audio issues fix"
date: 2026-02-21 18:20
categories: ["computer", "misc"]
---

This one isn't a regular blog post. It is for people who have issues with Bluetooth audio on
`Realtek rtl8852bu`. This will be a quick one.

## Trivia

I own `Chuwi Corebook X` with `Ryzen 5-7430U` that features an onboard, soldered `Realtek rtl8852bu`
NIC/Bluetooth combo card. The Bluetooth is wired via USB, but that's beside the point...

Ever since I set up Debian on it, I always had issues with Bluetooth audio, to the point
that I stopped using Bluetooth headphones as it would drive me nuts. The issue was that, totally at
random, the audio would start stuttering, but in a different way. It would sound as if audio
packets had lost order, as if later packets would mix with previous ones (hard to explain).
Once such a state had been "entered," there was no stopping it until I paused the music/videos for a
while.

I had multiple attempts at resolving this. I tried:

- building a custom up-to-date kernel,
- messing with Bluetooth driver parameters,
- latency tuning,
- codec switching,
- disabling Wi-Fi, or switching bandwidths,
- hardware dependencies like testing under stress or by removing any USB devices from the laptop...

Nothing worked... The main issue was it occurring completely at random, even though I have the
laptop on my desk, there is not even a meter between the laptop and the headphones.

## Solution

I've found
[this post on the Fedora forum](https://discussion.fedoraproject.org/t/bluetooth-audio-stuttering-during-wifi-activity-on-rtl8852ce/142165/12)
that described similar issues to mine, though for a different Realtek chip. TL;DR: the issue was
that the firmware binary had been updated and introduced a regression. I decided to check whether
that might be the case for my chip too. Here's what I've done...

### Debugging

The `dmesg` shows which firmware files are being loaded:

```text
timax in ~ λ sudo dmesg | grep -i "rtl_bt"
[170179.748558] Bluetooth: hci0: RTL: loading rtl_bt/rtl8852bu_fw.bin
[170179.748922] Bluetooth: hci0: RTL: loading rtl_bt/rtl8852bu_config.bin
```

On the filesystem, they exist at `/lib/firmware/rtl_bt/`:

```text
timax in ~/Development/linux-firmware-git on main λ ls /lib/firmware/rtl_bt/rtl8852bu*.bin
/lib/firmware/rtl_bt/rtl8852bu_config.bin  /lib/firmware/rtl_bt/rtl8852bu_fw.bin
```

They are a part of `firmware-realtek` package (`non-free-firmware`):

```text
timax in ~/Development/linux-firmware-git on main λ sudo apt search firmware-realtek
firmware-realtek/stable,now 20250410-2 all [installed]
  Binary firmware for Realtek network and audio chips
```

Now, while Debian groups and packs those binaries as a separate packages, they are taken from the
[`linux-firmware`](https://git.kernel.org/pub/scm/linux/kernel/git/firmware/linux-firmware.git/tree/rtl_bt)
repository, where they are stored as binary blobs (precompiled binaries). I did download the
"realtek-part" of the repository (along with the history), so I could test older binaries:

```bash
mkdir linux-firmware-git && cd linux-firmware-git
git init
git remote add origin https://git.kernel.org/pub/scm/linux/kernel/git/firmware/linux-firmware.git
# The below allows downloading only selected contents, the whole repo is massive
git config core.sparseCheckout true
echo "rtl_bt/" >> .git/info/sparse-checkout
# Pulling history for last 1000 changes
git pull --depth 1000 origin main
```

Then I checked history to see all the commits that messed with the files that interested me:

```text
timax in ~/Development/linux-firmware-git on main λ git log --oneline -- rtl_bt/rtl8852bu_fw.bin
8bcc91d13bbe rtl_bt: Update RTL8852B BT USB FW to 0x42D3_4E04
c1a6a1a2030f rtl_bt: Update RTL8852B BT USB FW to 0x098B_154B
bb5d129bceaa rtl_bt: Update RTL8852B BT USB FW to 0x0474_842D
9c2bf7af8bc2 rtl_bt: Update RTL8852B BT USB FW to 0x049B_5037
bf3697e4c2a8 rtl_bt: Update RTL8852B BT USB FW to 0x04BE_1F5E
59def907425d rtl_bt: Update RTL8852B BT USB FW to 0x0447_9301
0c4f8161e1d0 rtl_bt: Update RTL8852B BT USB FW to 0x048F_4008
0061a2dde6c3 rtl_bt: Update RTL8852B BT USB firmware to 0xDBC6_B20F
fe3ec816766a rtl_bt: Add firmware and config files for RTL8852B
```

...and then it was a matter of comparing which revision I have locally installed:

```text
# This is the one installed locally
timax in ~ λ md5sum /lib/firmware/rtl_bt/rtl8852bu_fw.bin
f6ab38a34886fd6876c8c30d9fc3a18c  /lib/firmware/rtl_bt/rtl8852bu_fw.bin
[...]
timax in ~/Development/linux-firmware-git/rtl_bt on main λ md5sum rtl8852bu_fw.bin
7445c08fbf38c3022fe35becd8c980b8  rtl8852bu_fw.bin
timax in ~/Development/linux-firmware-git on main λ git checkout 8bcc91d13bbe^
[...]
timax in ~/Development/linux-firmware-git on main~100 λ md5sum rtl_bt/rtl8852bu_fw.bin
cc2e828f1963b095a27703cd853a4dc0  rtl_bt/rtl8852bu_fw.bin
timax in ~/Development/linux-firmware-git on main~100 λ git checkout c1a6a1a2030f^
Previous HEAD position was 89cd30bfd784 Merge branch 'robot/patch-0-1763634312' into 'main'
HEAD is now at c8af472e05cb Merge branch 'robot/pr-0-1745527302' into 'main'
timax in ~/Development/linux-firmware-git on main~324 λ md5sum rtl_bt/rtl8852bu_fw.bin
f6ab38a34886fd6876c8c30d9fc3a18c  rtl_bt/rtl8852bu_fw.bin
```

This confirmed I was two versions behind compared to upstream.

### Fix

I checked out back to the `HEAD` to have the latest firmware binary for my card:

```text
timax in ~/Development/linux-firmware-git on main~324 λ git checkout main
Previous HEAD position was c8af472e05cb Merge branch 'robot/pr-0-1745527302' into 'main'
Switched to branch 'main'
```

Then I've backed up the binaries I had locally, and copied the ones from `linux-firmware`
to where the system ones reside:

```bash
sudo cp /lib/firmware/rtl_bt/rtl8852bu_fw.bin /lib/firmware/rtl_bt/rtl8852bu_fw.bin.old && \
sudo cp rtl_bt/rtl8852bu_config.bin /lib/firmware/rtl_bt/
```

_Note that I didn't copy the config file, as the `linux-firmware` does not have one. I reused
one from `firmware-realtek`._

After that, it was a matter of reloading the driver and testing.

```bash
sudo modprobe -r btusb
sudo modprobe btusb
```

### Afterwords

The above fixed the issue for me. I've been testing this for over an hour now, with not a single
occurrence. I had two temporary drops in that time, but I guess it's Realtek being Realtek.

## Debian bug tracking

I've also submitted the issue to Debian bug tracking system:
<https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=1128598>
