// 定義資料介面 (這樣兩個檔案都能用同一個 Type)
// 後端還沒串接前，先用這個資料檔案當作公告資料
export interface Announcement {
  id: number;
  date: string;
  type: string;
  content: string;      // 列表顯示的標題
  fullContent?: string; // 只有點進去才看得到的詳細內容
}

// 這是唯一的資料來源 (Single Source of Truth)
export const announcementsData: Announcement[] = [
   {
    id: 7,
  date: '115.04.13',
  type: '系統公告',
  content: '系統更新公告：115/4/13 上線功能說明 🆕',
  fullContent: '20260413 系統新上線功能如下 \n1.申請案件辦理結案過程中所需表單，請至系統之 「補助申請」 / 「申請案件查詢與列印功能」下載使用。\n已上線表單如下：\nA. 勘查審查類\nA1 外出照片攜帶表\nA2 施工前後照片\nA3 書面審查表.pdf\nA4 功能測試現地勘查報告書.pdf\n\nB. 經費與預算類\nB1 工程預算書.pdf (最多一次30筆)\nB2 管路補助金額明細表\nB4 領款收據.pdf\n\nD. 其他\nD1 住址標籤.xlsx\nD2 封面.pdf\nD3 切結書收據結案申報書.pdf(最多一次30筆)\n\n另C. 設計與地籍類，團隊將儘快完成功能並上線。\n\n2.申請案件各處自定義標註功能，請至系統之 「補助申請」 / 「補助案件申請」/申請案列表 頁面下進行。\n\n(1) 請點選需標註自定義之申請案，進入該案件進行定義(如115年度第一批、115年度第二批…等)。\n(2) 篩選條件列，提供自定義分類搜尋功能，請輸入自定義分類名稱，即可搜尋到相關案件。\n '
  },
  {
    id: 6,
  date: '115.03.13',
  type: '系統公告',
  content: '115年度 管灌設施補助宣導摺頁 下載 ',
  fullContent: `
    <div class="pdf-announcement">
      <p>115年管灌設施補助宣導摺頁已正式發佈，歡迎相關人員下載查閱 。</p>
      
      <div class="pdf-thumbnail" style="margin: 15px 0;">
        <a href="https://drive.google.com/file/d/1XaMky1eUa24kzVublY7mffOfvGDAu-aV/view?usp=sharing" target="_blank">
          <img src="https://drive.google.com/thumbnail?id=1XaMky1eUa24kzVublY7mffOfvGDAu-aV&sz=w300" 
               alt="115年度管灌設施補助宣導摺頁" 
               style="border: 1px solid #ddd; border-radius: 4px; cursor: pointer; transition: 0.3s;"
               onmouseover="this.style.opacity='0.8'" 
               onmouseout="this.style.opacity='1'">
        </a>
      </div>

      <div class="download-link">
        <a href="https://drive.google.com/file/d/1XaMky1eUa24kzVublY7mffOfvGDAu-aV/view?usp=sharing" 
           target="_blank" 
           style="color: #2c3e50; text-decoration: underline; font-weight: bold;">
           👉 點此下載：115年管灌設施補助宣導摺頁.pdf 
        </a>
      </div>
    </div>
  `
  },
  {
    id: 5,
  date: '115.03.05',
  type: '系統公告',
  content: '115年度 推廣管路灌溉設施作業指引 ',
  fullContent: `
    <div class="pdf-announcement">
      <p>115年度推廣管路灌溉設施作業指引已正式發佈，歡迎相關人員下載查閱 。</p>
      
      <div class="pdf-thumbnail" style="margin: 15px 0;">
        <a href="https://drive.google.com/file/d/1ciYxgwwkq0yvdkmd6SymoiQLuoHFGE73/view?usp=sharing" target="_blank">
          <img src="https://drive.google.com/thumbnail?id=1ciYxgwwkq0yvdkmd6SymoiQLuoHFGE73&sz=w300" 
               alt="115年度推廣管路灌溉設施作業指引" 
               style="border: 1px solid #ddd; border-radius: 4px; cursor: pointer; transition: 0.3s;"
               onmouseover="this.style.opacity='0.8'" 
               onmouseout="this.style.opacity='1'">
        </a>
      </div>

      <div class="download-link">
        <a href="https://drive.google.com/file/d/1ciYxgwwkq0yvdkmd6SymoiQLuoHFGE73/view?usp=sharing" 
           target="_blank" 
           style="color: #2c3e50; text-decoration: underline; font-weight: bold;">
           👉 點此下載：推廣管路灌溉設施作業指引115年版.pdf 
        </a>
      </div>
    </div>
  `
  },
  {
    id: 4,
    date: '115.01.08',
    type: '系統公告',
    content: '114 年度未結案件移轉說明 ',
    fullContent: '系統會自動將 114 年度未結案件移轉過去。\n為避免資料在轉換中有誤，麻煩各位夥伴先進在編輯案件時協助確認以下幾點：\n*進入案件後，請先檢視左方功能列的第 1 至第 8 步驟，確認移轉過來的內容是否正確。\n*確認完畢後，請從第 1 步開始依序點擊「下一步」來完成儲存程序。\n*重要提醒：若您有需要修改「土地、灌溉型式或材料」等欄位，因系統邏輯關係，請記得連同「灌溉調控設施」及「田間管路」一併重新填寫。\n\n新系統上線初期若有不便之處，還請各位多多包涵，謝謝！\n'
  },
  {
    id: 3,
    date: '114.12.26',
    type: '系統公告',
    content: '系統正式上線公告:正式上線日期為「115年1月9日」',
    fullContent: '新系統正式上線日期為「115年1月9日」。\n1、過渡期間，舊系統會繼續上線到115/1/31，於115/1/5 ~ 1/31 這段期間若使用者仍在「舊系統」改資料，新系統 不會 有紀錄。 \n\n2、115年材料表匯入前，如管理處已有新增案件至步驟5田間管理，則需要在材料表匯入後再更新一次"自動帶入材料"。'
  },
  {
    id: 2,
    date: '114.01.02',
    type: '系統公告',
    content: '承辦窗口資訊',
    fullContent: '新系統有操作問題可以洽詢農工中心以下窗口\n(1)林佩瑩小姐 電話：03-4521314#221 \n(2)陳力苑小姐 電話：03-4521314#231。'
   }//,
  // {
  //   id: 1,
  //   date: '114.01.02',
  //   type: '停機公告',
  //   content: '2025/01/05 ~ 2025/01/08 18:00系統將進行資料更新',
  //   fullContent: '為提供更優質的服務，系統將於2025/01/05 ~ 2025/01/08 進行匯入114年度申請案。\n並清空114年12月30日～115年1月4日於新系統新增的測試案件。'
  // }
];