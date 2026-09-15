# 420 Smoking — RE_Kenshi版（開発中）

本プロジェクトはRE_Kenshi版に特化して開発します。基盤MODと煙プラグインの2つを使用します。

## 導入

1. RE_Kenshiを導入する。確認環境はKenshi 1.0.65 / RE_Kenshi 0.3.5。
2. `build/420_Smoking` と `build/420_Smoking_RE` をゲームの `mods` フォルダへ配置する。
3. MOD一覧で `420_Smoking`、`420_Smoking_RE` の順に有効にし、ゲームを再起動する。

煙MODのフォルダには `420_Smoking_RE.mod`、`RE_Kenshi.json`、`SmokingSmoke.dll` が必要です。`420_QA` は開発用の開始条件です。

## 煙の動作

- 対象は `420_smoke_chillum`、`420_smoke_joint`、`420_recline_chillum`、`420_recline_joint`。
- 12秒ループの8–11秒に口から煙を出し、先端煙は対象動作中に継続する。
- 呼気の設定は72粒子/秒、基準サイズ1.56。増量設定に対するユーザーの実機確認済み。見た目の倍率を測定した値ではありません。
- 発生済みの煙は薄れて消える。ワールドリセット時に一時状態をクリアする。
- 拡張を無効にした基盤MODは煙なし。静止煙の試作は不採用です。

ゲーム内の `kenshi_smoke1` マテリアルを実行時に複製して使用します。元のゲームテクスチャ・シェーダーは再配布しません。実機確認の範囲はプロジェクトの `qa/user_confirmation_2026-09-15.md` に記録しています。

## ビルド

プロジェクトルートで `tools/build_re_smoke.ps1` を実行します。ローカルのVC2010 x64、Windows SDK 7.1、公式KenshiLib_Examples_deps、Boost 1.60を使用します。参照パスはスクリプトに記載しています。FCSの煙MODは `tools/build_re_smoke_mod.py` で生成します。

ソースの正本は `src/re_smoke/SmokingSmoke.cpp` です。

Source license: GPL-3.0-or-later. KenshiLib and its dependencies retain their own licenses. This project has not modified or rebuilt KenshiLib or RE_Kenshi.
