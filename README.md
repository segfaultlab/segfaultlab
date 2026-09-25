<picture>
  <source media="(prefers-color-scheme: dark)" srcset="profile/dark.svg">
  <img alt="koko@segfaultlab: neofetch" src="profile/light.svg" width="100%">
</picture>

### `$ ls ~/projects`

| 项目 | 做什么 | 技术 |
| --- | --- | --- |
| [**crossbuild-agent**](https://github.com/segfaultlab/crossbuild-agent) | 给它一个开源 C/C++ 项目，Agent 自己读构建系统、试编译、读报错、查经验库、改配置，直到 ARM64 交叉编译通过。是否成功由程序独立验收 ELF 产物，不靠模型自述 | Python · LangGraph · MCP · RAG |
| [**CrossShellNext**](https://gitcode.com/OpenHarmonyPCDeveloper/CrossShellNext) | 对标 PuTTY 的多协议终端，从零设计：C++ 协议层、NAPI 异步桥接、ArkTS 界面，支持 SSH / Telnet / Serial / SFTP | C++17 · libssh2 · OpenSSL |
| [**OpenHarmony update_updater**](https://gitee.com/openharmony/update_updater) | 升级子系统：flashd 刷写、差分与连续升级、升级包 SHA256 校验，C++ 接口向 Rust 过渡 | C++ · Rust FFI · Python |
| **PyTorch on musl/aarch64** | 官方只发 glibc 版本，把 PyTorch CPU 推理运行时移植到 musl + ARM64，打通到 `import torch` 和 TorchScript 推理 | Clang/LLVM · CMake · musl |

### `$ cat ~/.stack`

<img src="https://skillicons.dev/icons?i=cpp,c,rust,py,cmake,linux,docker,git,fastapi,vue,threejs&perline=11" alt="C++ C Rust Python CMake Linux Docker Git FastAPI Vue Three.js">

```text
$ ./life
Segmentation fault (core dumped)   # 然后开始 debug
```
