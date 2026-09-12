# Kenshi 420 喫煙MOD — 開発中

**完成版ではありません。ゲーム内検証を進めているアルファ版です。**

仕様の正本は `Kenshi_喫煙MOD_仕様書.md`。バフ・デバフは対象外です。

## 作成したもの

- チラム、ジョイント、麻紙、道具置き付き喫煙席の独自モデルとテクスチャ。
- 人間男性用のチラム・ジョイント喫煙アニメーション（各8秒）。
- 麻 → 紙、麻＋紙 → ジョイントの製作データ。
- 2種類の製作設備と2種類の喫煙席の試作データ。
- 紙専用収納箱。標準のハシシ収納箱を複製し、収納対象を紙に変更。
- 既存セーブを使わず検証するための `420_QA` 新規開始条件。

## 開発ファイル

| 場所 | 内容 |
| --- | --- |
| `src/create_assets.py` | Blenderのモデル生成ソース |
| `src/create_animations.py` | Blenderのアニメーション生成ソース |
| `tools/inspect_base.py` | ローカルのゲームデータを読み取り、参照元を確認 |
| `tools/build_prototype.py` | 既存モデルを使った消費検証用MODの生成 |
| `tools/build_mod.py` | 独自モデルと動作を組み込んだアルファ版の生成 |
| `tools/build_qa_start.py` | 専用の新規テスト開始条件を生成 |
| `assets/smoking_animation_work.blend` | モデル、元の人間骨格、制作中アニメーションを含む作業ファイル |
| `build/420_Smoking` | アルファ版。配布・完成版扱いは不可 |
| `build/420_QA` | 開発専用の開始条件。完成版には含めない |
| `qa` | プレビュー、検証記録、検証前設定のバックアップ |

ゲーム本体・元の人間モデル・参照用ゲームデータ・FCSのコピーは配布物に含めません。

## 仮の検証設定

設備は所有する建物の屋内設置を基本とします。屋外対応は設備ごとに検証して決めます。初期のゲーム検証用ビルドでは屋外も一時的に許可していましたが、生成ソースは屋内を基本とする設定に変更しています。

紙1個に麻1個、ジョイント1個に麻1個と紙1個。設備の生産倍率は検証用で、ゲームバランスの確定値ではありません。

喫煙席は、生産機能に消費材料を設定し、出力アイテムを空にした実験です。材料が減ること、材料切れで停止することはゲーム内で確認が必要です。データ生成成功は動作成功を意味しません。

道具はFCSの `special tool` を使って表示する試作です。Blenderプレビューの追従成功はゲーム内の追従保証ではありません。

## 完成までに必要な確認

- [ ] 紙とジョイントが設定数量で製作される。
- [ ] 喫煙席を設置でき、指定したキャラクターが利用できる。
- [ ] 喫煙中に対応する材料が消費される。
- [ ] 材料切れ・移動命令・戦闘で意図せず継続しない。
- [ ] ゲーム内でも道具が手に自然に追従する。
- [ ] 指や顔との重なりを調整する。
- [ ] 女性・他の対応種族を検証する。
- [ ] セーブ・ロードで製作・在庫・家具利用が維持される。
- [ ] 検証用設定を外し、説明文と導入手順を確定する。

## 参照した公開資料

- [Kenshi Mod Tools](https://github.com/Superfly-Johnson/kenshi-mod-tools) — MIT。`tools/vendor/kenshi.py` にUTF-8文字列長と現行ヘッダー読込への変更を加えています。
- [Kenshi gamedata/mod/save file format](https://steamcommunity.com/sharedfiles/filedetails/?id=797652627) — ファイル形式の参考。
- [kongyo-kenshi-tool](https://github.com/kongyo2/kongyo-kenshi-tool) — v17ヘッダー構造の参考。レコードの状態フラグはローカルの実データも照合しています。
- [Sanskriti Museum of Everyday Art](https://artsandculture.google.com/story/sanskriti-museum-of-everyday-art-sanskriti-museums/pAWxqPlaLq2EKA?hl=en) — 喫煙器具の素材・外観の参考。
