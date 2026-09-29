# Role Play faces

`mpfb.glb` is the example avatar from TalkingHead
(github.com/met4citizen/TalkingHead, commit b3e277b), made with MPFB in
Blender and licensed **CC0** (public domain). It is the only TalkingHead
sample we may use: the others (Ready Player Me, Avaturn, AvatarSDK, VRoid)
are non-commercial only, and staff training is commercial use.

Shrunk from 37 MB to 3 MB with gltf-transform, in this order (meshopt last,
or the other steps undo it):

    npx @gltf-transform/cli@4 resize mpfb.glb a.glb --width 1024 --height 1024
    npx @gltf-transform/cli@4 webp a.glb b.glb --quality 85
    npx @gltf-transform/cli@4 meshopt b.glb mpfb.glb --level high

Used only by `face-test.html` (Frank, 2026-09-29), a test page nothing links to.
