<picture>
  <source media="(prefers-color-scheme: dark)" srcset="profile/dark.svg">
  <img alt="koko@segfaultlab: neofetch" src="profile/light.svg" width="100%">
</picture>

### `$ cat ~/.stack`

<img src="https://skillicons.dev/icons?i=cpp,c,rust,py,cmake,linux,docker,git,fastapi,vue,threejs&perline=11" alt="C++ C Rust Python CMake Linux Docker Git FastAPI Vue Three.js">

### `$ ./snake --eat contributions`

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="profile/snake-dark.svg">
  <img alt="贪吃蛇吃掉贡献格子" src="profile/snake.svg" width="100%">
</picture>

### `$ cat /var/log/visitors | wc -l`

<img src="https://count.getloli.com/@segfaultlab?name=segfaultlab&theme=3d-num&padding=7&offset=0&align=top&scale=1&pixelated=1&darkmode=auto" alt="访客计数">

```text
$ ./life
Segmentation fault (core dumped)   # 然后开始 debug
```

<details>
<summary><code>$ cat .secret</code></summary>

```text
$ cat .secret
cat: .secret: Permission denied
$ sudo cat .secret
[sudo] password for koko:
koko is not in the sudoers file. This incident will be reported.
```

没拿到权限也没关系，答案其实早就写在上面的 backtrace 里了：`life.cpp:42`。

</details>
