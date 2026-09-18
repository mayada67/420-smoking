# 煙表示の再開検証（2026-09-15）

利用制限で中断した「Add smoking smoke animation」の最後の変更から再開。

## 今回確認したこと

- 最終の骨軸修正版DLLとゲーム導入先のSHA256が一致：`ACB87FE3DACE25A6EC5279BAF8E0FC0E58FAF1E4F0A61EFAE62D6FE853FDBA6B`。
- Kenshi 1.0.65 / RE_Kenshi 0.3.5。420_Smoking、420_QA、420_Smoking_REを有効にして起動。
- 専用セーブ `420_smoke_QA_20260913` をロード。ヘフト屋内の男性キャラクターがチラムを使用。
- 口の煙が顔の前方へ流れ、チラムの先端から細い煙が上がることを画面で確認。前回の下向きの呼気は再現しなかった。
- ログ上のアニメーション速度は1。約2秒ごとのサンプルで再生位置も約2秒進む。7.56秒で13粒、9.57秒で28粒、11.57秒で10粒。次ループも同じ傾向。
- `tools/check_smoking_timing.py` を再実行し、チラム・ジョイントとも12秒ループ、3秒保持、保持姿勢誤差0、ループ継ぎ目誤差0を確認。

## 証拠

- `re_smoke_axis_fix_ingame.png`：修正版の前向きの呼気。右下には利用者の動画ウィンドウが重なっている。
- `re_smoke_axis_fix_verified.log`：今回起動のプラグイン初期化と喫煙サンプル。
- `smoking_timing_roundtrip.json`：書き出し済みskeletonを再読込した検査。

## 残る検証

- ジョイント、女性・他種族の実ゲーム表示。
- 時間加速、一時停止、移動・戦闘・材料切れによる中断、ワールド再読込時の煙の後始末。
- 呼気の開始・終了境界のフレーム単位での実測。今回のログは約2秒間隔で、境界の厳密な実測ではない。
- MOD全体の製作・消費などの確認項目はREADMEを参照。

今回ソースやDLLの追加変更は不要だった。前回導入済みの最終修正を実機で確認した。検証セーブは上書きしていない。

## 利用者の指摘による停止区間の修正
口に道具を当てたままの保持では吸気終了が伝わらなかったため、吸気2–4秒、下降4–5秒、停止5–8秒、呼気8–11秒へ変更。両アニメーションの道具が下がった後の3秒保持を読み戻し検査し合格。DLL・skeletonはバックアップ後にゲームへ反映しハッシュ一致を確認。再起動時に利用者のEscapeでComputer Useが停止したため、新タイミングの実ゲーム確認は未完了。

## 停止区間の実ゲーム再確認
修正版DLLで専用セーブを再ロード。男性・チラムを約1秒間隔で14枚記録（hold_sequence_00～13.png、時刻はhold_sequence_times.json）。00は口に道具、01～04は道具を下げて口の煙なし、05～07で呼気、08は残煙、09で消失、10～12は次の吸気、13は道具を下げた状態。道具を下げた後に待ってから吐く順序を確認。3秒保持のデータ検査・通常速度のログと整合する。1秒間隔の画面記録なので境界のフレーム精度での実測ではない。ジョイントはデータ検査済みだが実ゲームの確認対象は今回もチラムのみ。

## 呼気の増量
利用者の希望で口の粒子発生を毎秒12→24、大きさ0.45→0.52へ変更。3秒の保持と8–11秒の呼気窓、先端煙は維持。ビルドと静的互換性検査に合格。導入DLLのSHA256はA615D384C24A0B2902D5865021382152F41E98644FB4E3F14DB10B7BB1583FCB。旧DLLはqa/before_more_exhaleへ保存。
増量版の実ゲーム確認：男性・チラムで、待機後の前向きの呼気が濃く広くなったことを確認。more_exhale_ingame.png、re_smoke_more_exhale_verified.logへ記録。

## Shared workbench and joint storage
- Both legacy benches (21/22) now use recipe crafting functionality 11 for paper and joints; new construction unlock exposes bench 21.
- Added joint-only storage 26 using the same vanilla hashish storage source as paper storage 25; research 30 unlocks both.
- Built 24-record mod; binary recipe/input/storage/unlock checks passed (qa/shared_workbench_checks.json).
- Installed mod and records.json; SHA256 matched. Prior files backed up to qa/before_shared_workbench.
- In-game crafting, storage operation and existing-save unlock availability have not been verified; game restart needed to load new mod data.

## Beanbag seats
- Added seats 27/28, part 56, cloth material 57; research 30 unlocks both. Original seats preserved.
- Source src/create_beanbag.py and assets/beanbag.blend; preview qa/beanbag_preview.png.
- 28-record build, binary readback and reference checks passed. Deployed mod and three new assets. Backup qa/before_beanbag.
- In-game placement, pathing, seated clipping and existing-save unlock availability remain unverified.

## Beanbag facing correction
- User reported sideways seating; observed character facing sideways through the beanbag back in game.
- Changed only operator rotations on buildings 27/28 to (w,x,y,z)=(sqrt(0.5),0,-sqrt(0.5),0), a -90 degree yaw.
- Build/readback/reference and shared workbench checks passed. Record diff limited to 27/28. Installed mod hash FB1C9704D9851048A3F33DDE0E098A4280126B3B403A2D74F866770479A86E8B matches build.
- Corrected game appearance pending restart and user retest. Existing placed node rotations may persist in saves; test a newly placed seat if needed.


## Facing reversal and construction rendering
- User retest confirmed prior yaw was 180 degrees backward. Buildings 27/28 now use +90 Y quaternion, reversing prior correction.
- Game log at 17:32-17:33 repeatedly reports missing bound vertex slot for beanbag StaticObject_10f material.
- Local objects.hlsl requires COLOR0 when DUAL_TEXTURE/COLOURING is defined; custom meshes do not author vertex colors. Materials 51/57 now use BuildingShader.DEFAULT, with redundant secondary texture references removed. This addresses a concrete vertex layout mismatch; construction visibility still needs in-game retest.
- Sources: installed fcs_enums.def (BuildingShader), data/materials/deferred/objects.hlsl and construction.material, kenshi.log. No claim of prior Deep Research.
- Build/readback/reference/shared crafting checks passed; updated mod deployed. Backup qa/before_seat_render_fix.
