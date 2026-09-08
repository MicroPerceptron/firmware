# Firmware

Vendor firmware for MicroPerceptron projects, pinned independently of operating
system source. Clone this repository or consume an exact commit as a submodule;
all catalogued binaries are present in the checkout. No per-vendor fetch step is
needed, and verification works offline.

The catalog contains seven Intel images pinned by Kore and the Realtek RTL8922AE
image pinned by Kore PR #936. The
layout accepts additional vendors and device families as their firmware is
reviewed; inclusion does not imply that a consuming driver supports the device.

| Family | Images | Original license notices |
| --- | --- | --- |
| Intel NPU (`intel/ivpu`) | VPU 37xx, 40xx, 50xx | [40xx](LICENSES/intel-npu-fork.txt), [37xx / 50xx](LICENSES/intel-npu-upstream.txt) |
| Intel GPU (`intel/xe`) | MTL / DG2 GuC | [Intel GPU](LICENSES/intel-guc.txt) |
| Intel GPU (`intel/xe`) | LNL / BMG GuC | [Intel Xe](LICENSES/intel-xe.txt) |
| Realtek Wi-Fi (`realtek/rtw89`) | RTL8922AE format-4 container | [Realtek](LICENSES/realtek-rtw89.txt) |

The Realtek container is stored under the consumer name `rtw8922a_fw.bin`;
its upstream name is `rtw8922a_fw-4.bin`. It does not contain a cut-A image.
The catalog preserves PR #936's exact selected pin, not its commented fallback.

## Catalog and verification

[`manifest.toml`](manifest.toml) maps each stable image ID to its vendor, family,
repository-relative filename, byte size, BLAKE3 digest, exact upstream source
commit/path, and license entry. License entries retain their own source and
BLAKE3 digest. Original binary bytes and notice texts are preserved unchanged.

With Python 3.11+ and `b3sum`:

```sh
python3 verify.py
```

A consumer can supply its existing hasher instead:

```sh
python3 vendor/firmware/verify.py --hasher 'cargo run -q -p kore-b3sum --'
```

Consumers should pin the submodule commit, retain any device-specific acceptance
pins and runtime verification, and include the applicable license notices in
images or packages that redistribute firmware. Initialization uses
`git submodule update --init vendor/firmware`, never `--remote` during a build.

## Adding or updating firmware

Place original bytes under `<vendor>/<family>/`, copy the exact accompanying
license/notice text into `LICENSES/`, and add both provenance and digests to the
catalog. Use an immutable upstream commit, inspect the applicable redistribution
terms, and run the verifier. A firmware update is an explicit reviewed commit;
consumer repositories advance their submodule only when ready to accept it.
Do not import firmware without an applicable redistribution grant.

Ordinary Git stores the initial small catalog. If its size grows substantially,
versioned release bundles can replace blob storage behind the same catalog;
consumers must still verify immutable digests.

## Licensing

There is **no blanket license for the firmware collection**. Each binary remains
under the vendor terms linked above and mapped in the catalog; moving it to a
separate repository does not change those terms. Preserve the relevant notices
when redistributing binaries. The verification tools, CI configuration, and this README are provided under
[0BSD](LICENSE.tools), which does not apply to vendor firmware or notices.
