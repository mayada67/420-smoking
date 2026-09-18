# Kenshi 建築・家具MOD仕様調査

調査日: 2026-09-15。対象: この環境のKenshiと420_Smoking、新しい喫煙用ビーズクッション。

## 結論

1. 椅子の向きは「椅子の背もたれから座面の前へ向かう方向」と「座った人物の前方」の相対関係で判定する。画面やワールドに対する90度ではない。現在の+90度設定は前回の逆向き報告への修正候補で、実機合格は未確認。
2. 設置前の赤・緑プレビューと、予約確定後の建設中表示は別のマテリアル定義を持つ。透明問題を一括して『材質変更で修正済み』とは扱えない。
3. 過去のログに新しい椅子の描画エラーがある。DUAL材質と頂点色を出力しないメッシュの不整合が有力。ただしログの材質名はStaticObjectであり、建設中表示が消える直接原因まで証明していない。
4. 建設中の網目はUV・足場テクスチャ・高さ・進捗で描画される。単色の完成品が見えても建築予約の表示保証にはならない。
5. 家具パーツのpassable=trueはクリック判定だけに衝突形状を使う設定。椅子を障害物として迂回する保証はない。

## 調査方法と限界

公開Web資料、ゲーム同梱のfcs.def/fcs_enums.defとシェーダー、導入済みBlenderエクスポーター、生成済みMODレコード、ゲームログを照合した。このセッションに専用Deep Research呼び出しツールは見つからず、専用機能を実行したという意味での報告ではない。

ゲーム本体の建築処理ソースは読めていない。公開仕様が不足する実行時挙動は推論と明示する。今回ゲーム操作・追加修正・再導入はしていない。以前のテスト記録は今回の再検証と区別する。

純正データ・同梱コメントも実行時の正しさを保証しない。ユーザー指摘の通り、本体由来の不具合も候補に残す。通常家具は対照として使い、通常家具でも再現するか、カスタム家具に固有かを比較する。

## 1. 建築データの構成

FCSは開発チーム自身も使うゲームデータ編集ツールである。[Lo-Fi Games公式説明](https://lofigames.com/ja/community-update-41-fcs-update-kenshi-2-raptors/)

| データ | 主な役割 | このMOD |
|---|---|---|
| BUILDING | 建築メニュー、建築資材、設置条件、パーツ・機能・ノードの参照 | 27=ハシシ用、28=ジョイント用 |
| BUILDING_PART | 表示メッシュ、衝突XML、階層、接地条件、材質 | 56=ビーズクッション |
| MATERIAL_SPEC | テクスチャ、シェーダー種類、足場の繰り返し量 | 57=汚れた布 |
| BUILDING_FUNCTIONALITY | 使用アニメーション、入出力、使用者数 | 13/14 |
| 使用ノード | 使用位置と回転を持つ子インスタンス | 420_operator → 1183-gamedata.base |

根拠: ゲーム同梱fcs.defのBUILDING、BUILDING_PART、BUILDING_FUNCTIONALITY節、および生成レコード。

### 建築資材と見た目

construction参照は建築に必要なITEM。表示材質はmaterial参照。両者は別であり、布を建築費に指定してもモデルが布の見た目に変わる仕組みではない。build materialsとbuild speed multにも別フィールドがあるため、参照の個数だけで所要時間を断定しない。

partsのグループ0は各パーツを絶対確率で選ぶ。他のグループはグループ内から選択する。今回のparts=[0,100,0]は常時採用を意図した構成。

### 階層と材質継承

building floor=0は基本パーツ。interior参照はキャラクターが屋内にいる時だけロードする内装パーツ。小型家具の本体を誤って内装・上階側へ置くと表示条件が変わり得る。現在のパーツ56はfloor=0、椅子のpartsから直接参照している。

パーツに材質がない場合は建物側へ継承する。material match等もあるため、複製元の参照が残っていないか確認する。現在56は57を明示参照。

## 2. 建築の各表示段階

| 段階 | 根拠となる定義 | 分けて確認すること |
|---|---|---|
| 設置前プレビュー | forward/previewbuilding.materialのredbuilding / greenbuilding / bluebuilding | 移動・回転中の形が見えるか |
| 予約確定後・未着工 | deferred/construction.material、objects.hlsl | 進捗0%でも場所が判別できるか |
| 建設途中 | 同上のconstructionState、upperPos、scaffoldTiling | 複数進捗で表示が破綻しないか |
| 完成後 | 通常のオブジェクト描画 | 本体・影・選択が正常か |

これは同梱スクリプトから分かる描画経路の区別。ゲームが個々の状態でどの派生材質を選ぶかの全分岐は未確認。

### 建設中表示の重要項目

- fcs.defはbuilding heightを建設シェーダー計算用の高さと説明している。現在10。モデルの実寸と合わせて扱う。
- scaffolding tex scaleは建設中足場テクスチャの繰り返し量。現在8。
- objects.hlslはUVにscaffoldTilingを掛けて足場テクスチャを読む。対象部分ではアルファ値0.7未満の画素を破棄する。
- 高さ計算はposition.yとupperPosを使用。ゼロ高さや不整合な座標は点検対象。ただし現在値10が透明化原因だという証拠はない。
- したがってUVが一点に潰れる、足場テクスチャが読めない、必要な頂点属性が欠ける、といった問題を別々に切り分ける必要がある。

今回のメッシュはUVを作成しており、UV欠如とは断定できない。材質を変更しても、この網目表示は実機確認が必要。

## 3. 描画エラーとDUAL材質

fcs_enums.defのBuildingShaderはDEFAULT=0、ALPHA=1、FOLIAGE=2、DUAL=3、EMISSIVE=4。

objects.hlslの頂点入力は位置・法線・UV・接線を要求し、COLOURINGまたはDUAL_TEXTUREの分岐ではCOLOR0も要求する。インスタンス描画では追加の行列入力もある。このため『bound vertex slotエラーは必ず頂点色』とは言えない。

しかし今回の旧材質はDUAL、メッシュ生成は頂点色を用意せず、導入済みエクスポーターのexport_color既定値はfalseだった。組み合わせに不整合があると考える根拠は強い。[エクスポーター作者のオプション説明](https://lucius64.github.io/kenshi_io_blender/Option_description.html)でも頂点色出力を独立したオプションとしている。

17:32:11のkenshi.logには420_beanbag_clothを含むStaticObject材質と、必要な頂点スロットが見つからないRenderingAPIExceptionが連続している。これは過去の実行時エラーの証拠であり、修正後の再発・解消の証拠ではない。

現在51/57はDEFAULT=0、第二テクスチャ類は空。単一の布材質を使う設計として妥当な修正候補。ただしConstruction_Dualはフラグメント側を差し替え、Construction_VPを継承している。通常描画の頂点色エラーをそのまま建設中経路に当てはめない。

## 4. 座る方向と位置

判定基準は椅子自身の前後。背中が背もたれ側、膝・顔が座面の開いた側を向くこと。ワールドの北や画面右は基準にしない。

概念的には、キャラクターの見える向きは建物の配置回転、使用ノードのローカル回転、アニメーションの基準姿勢の合成になる。メッシュの前方も書き出し座標変換を受ける。これは座標変換としての整理であり、ゲーム内部の厳密な行列乗算順序を確認した記述ではない。

fcs.defはnodesに位置と4成分回転を定義する。自作バイナリwriterは4成分をその順序で保存するだけで、順序の正しさ自体を保証しない。現在の実装はw,x,y,zとして[0.70710678,0,0.70710678,0]を設定している。

前回記録では、メッシュを再インポートした時の背もたれはBlender +Y側、前は-Y側。-90度ノード変更でユーザーが『90度動いたが180度逆』と報告したため、+90度へ変更済み。この経緯は今回の椅子に対する修正根拠であり、『Kenshiの椅子は全部+90度で正しい』という一般仕様ではない。

導入済みエクスポーターの骨格処理にもY-upへの変換と骨軸補正がある。メッシュ・骨格・衝突の座標を同一と仮定しない。[作者のツール説明](https://lucius64.github.io/kenshi_io_blender/)ではmesh/skeleton/colliderを別の入出力対象としている。

## 5. 衝突・設置・経路

fcs.defによる区別:

- BUILDING_PART.passable=true: 衝突形状はクリックにのみ使用。
- affects footprint: 設置できる場所の判定に影響。
- above ground / ground type / footprint vertical: 接地条件。
- BUILDING.path mode: 通り抜け、投影障害物、障害物、上を歩ける構造などの経路設定。
- is interior furniture=true: プレイヤー設置時に屋内専用。
- scale: 建物と衝突を全体拡縮。

現在56はpassable=trueかつaffects footprint=true。この二つは同じ意味ではない。椅子をクリックでき、建設できても、人物が椅子を避けるとは限らない。使用ノードまで接近できることと、家具を不自然に貫通しないことの両方を実機で確認する。

## 6. 一個セットして使い続ける仕様

consumesの第1値は最大保管個数、第2値は入出力比。現在13/14は[1,100,0]。これは1個の入力上限を表すが、『絶対に消費しない』というフラグではない。

現在の機能はproducesがなく、ハシシが減らないことはユーザー報告済み。ただしハシシ・ジョイント双方の長時間使用、作業解除、再ロードまでの非消費保証は未検証。

椅子本体のhas inventory=false、storage size=18×18と、機能側の入力上限1は別項目。入力枠を1個にする目的に対して、汎用収納サイズだけを1×1へ変えるのは根拠が不足する。

## 7. セーブと検証手順

既設家具の子ノードがMOD更新時に常に再生成されるかは、今回の一次資料では確定できない。インポート必須とも不要とも断定しない。既設と新設を分けて比較する。

1. 導入版を明示し、ユーザーのセーブ完了後にゲームを再起動。
2. 同じ部屋に通常の椅子、新ハシシ椅子、新ジョイント椅子を比較配置。
3. 設置前、確定後0%、建設途中、完成後をそれぞれ記録。
4. 新椅子を異なる配置角度で試す。背もたれに背中が向き、足が前に出ることを確認。
5. 着席位置・高さ・腕の貫通・接近経路・立ち上がりを確認。
6. 既設椅子と新設椅子を比較し、保存・再ロード後も同じか確認。
7. 各種1個で複数ループ使い、在庫数・入力枠・煙のタイミングを確認。
8. そのテスト時刻以降のログで描画例外を調べる。過去ログの残存を再発と誤認しない。

失敗時は、通常椅子との比較、メッシュだけ交換、材質だけ交換、UV・高さ・足場倍率の比較という順で、一度に一要素ずつ切り分ける。ゲーム全体のpreviewbuilding.material変更を最初の対策にはしない。

## 根拠ファイル

- [fcs.def](<C:/Program Files (x86)/Steam/steamapps/common/Kenshi/fcs.def:411>): 建物、機能、パーツ、材質のフィールド説明。
- [fcs_enums.def](<C:/Program Files (x86)/Steam/steamapps/common/Kenshi/fcs_enums.def:36>): BuildingShader列挙。
- [previewbuilding.material](<C:/Program Files (x86)/Steam/steamapps/common/Kenshi/data/materials/forward/previewbuilding.material:1>): 配置色材質。
- [construction.material](<C:/Program Files (x86)/Steam/steamapps/common/Kenshi/data/materials/deferred/construction.material:237>): 建設中材質。
- [objects.hlsl](<C:/Program Files (x86)/Steam/steamapps/common/Kenshi/data/materials/deferred/objects.hlsl:5>): 頂点入力、建設高さ、網目クリップ。
- [生成済みレコード](/E:/AI_Playground/420/build/420_Smoking/records.json): 現在の設定。
- [ビルド処理](/E:/AI_Playground/420/tools/build_mod.py:64): パーツと使用ノード設定。
- [メッシュ生成](/E:/AI_Playground/420/src/create_beanbag.py:56): UVと書き出し。

公開検索で見つかったWiki・掲示板回答は補助的な探索に使用し、上記の技術判断は同梱定義と作者の資料に基づけた。BetterBuildingPreviewのWorkshop本文はアクセス制限で読めず、根拠に採用していない。
