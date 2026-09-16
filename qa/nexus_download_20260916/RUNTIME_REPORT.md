# Nexus配布版の実機検証とRaces修正（2026-09-16）

## 結論

Kenshiを実際に4回起動して比較した。Coreの男性グリーンランダーのビーズクッション・チラム喫煙と煙は画面で確認できた。Races rc2には読み込みタイミングの不具合があり、設定1か所を修正すると種族登録が実行された。

環境: Kenshi 1.0.65（RE_Kenshi/kenshi_x64.exe）、RE_Kenshi 0.3.5、KenshiLib 0.5.1。

## Core配布版の確認

- Nexus ZIPから配置したSmokingSmoke.dllを使用。両DLLの読み込み成功。
- 既存の喫煙テストセーブquicksave（2026-09-15 18:41）をロード。
- ビーズクッション上の男性キャラクター、手に持ったチラム、姿勢変化と口元の煙をスクリーンショットで確認。
- 通常速度と5倍速で継続。ログには420_recline_chillumの時刻が1.266→3.268→5.301→7.308→9.310→11.329秒と進み、粒子数が3→7→7→7→100→113へ増える記録がある。これは周期の進行を裏付けるが、全フレームの計測ではない。
- 今回のログにSmoke disabled after renderer errorの記録なし。
- 右クリックによる移動指示は操作受付を確認できず、中断動作の合格判定は行わない。
- 他の席・ジョイント・女性・全種族・製作・セーブ再ロードの網羅検証は今回未実施。
- 旧セーブ上の製作台に[ALPHA]が残る表示を観察。配布MOD自体の名称チェックとは区別する。

## Races不具合

rc2のRE_Kenshi.jsonはPluginsを使用していた。ログでhook installedは出るが、ゲーム内へ入ってもapplied toの行は出ない。

同じDLLと同じMOD構成のまま、設定だけをPreloadPluginsへ変えると、ゲームのデータ後処理時に登録コードが実行される。比較ログでは登録処理が32.533秒、通常のpost-load開始が32.660秒。この順序から、通常ロードではフック設置が間に合わないことを確認した。

| 比較 | 実機ログ |
| --- | --- |
| rc2そのまま・対象追加種族なし | hook installedのみ。適用ログなし |
| PreloadPlugins・対象追加種族なし | applied to 0 existing supported races |
| PreloadPlugins・2B有効・Races有効 | applied to 2 existing supported races |
| PreloadPlugins・2B有効・Races無効 | applied to 0 existing supported races |

2B.modには2Bと2B Poseの2つのRACEレコードが存在する。今回確認したのは登録処理の実行と件数であり、2Bの喫煙姿勢の見た目までは確認していない。

RE_KenshiのPreloadPluginsはMOD無効時もDLLを読む。Racesのアニメ定義がデータベースに存在しなければ登録しない仕組みが、最後の比較で機能した。DLL自体を読み込ませたくない場合はゲーム終了後にMODフォルダをmods外へ移す。

## 修正物

- dist/420_Races_0.1.0-rc3_candidate.zip（Nexus未アップロード）
- ランタイム差分はmods/420_Races/RE_Kenshi.jsonのみ。DLL、Races.json、MODバイナリはrc2と同一。
- READMEとビルド説明を検証結果に合わせて更新。SHA256マニフェスト再生成・全件照合・ZIP CRC検証済み。
- 生成スクリプトもPreloadPluginsへ修正し、チェック・パッケージ処理に旧設定を拒否する検証を追加。
- tools/check_unified_races.pyは修正後も合格。

## 最終状態

ゲームは検証終了後に閉じた。ゲーム内セーブは作成・上書きしていない。画面設定とsettings.cfgは開始前へ復元。一時的な2Bの有効化は解除した。

インストール済みCoreは今回の配布版、Racesは修正版。ロード順は420_Smoking / 420_QA / 420_Smoking_RE / 420_Races。420_QAは開始前から有効だった開発用MODを維持している。通常プレイ向けの構成変更は別途判断する。

開始前のファイルはbefore_runtimeに保管。元のZIPとdistの既存配布ZIPは変更していない。

RE_Kenshiの起動中にはCould not initialize UIが一時的に出たが、その後メニュー表示に成功した。開始前のログにも同種の記録がある。これを今回のMOD固有の障害とは判定していない。

## 証跡

runtime_original.log / kenshi_original.log / runtime_preload_zero.log / runtime_preload_2B.log / runtime_preload_disabled.log / runtime_preload_disabled_mods.cfg / runtime_results.json。

静的チェックだけだったREPORT.mdの判断は、この実機レポートで更新する。配布Races rc2を正常動作と扱わない。
