import React, { useState, useEffect } from 'react';
import './post_report.css';
import Header from '../Header/header';

const PostReport = () => {
  const [reportContent, setReportContent] = useState('');
  const [feedback, setFeedback] = useState('');
  const [scores, setScores] = useState([0, 0, 0]); // スコアを3つ表示
  const [submittedFeedback, setSubmittedFeedback] = useState(null);
  const [pickedReports, setPickedReports] = useState(['', '', '']); // 入力サンプルを3つ表示
  const [userId, setUserId] = useState(null);
  const [isFeedbackCreating, setIsFeedbackCreating] = useState(false);

  // セッションストレージからuserIdを取得
  useEffect(() => {
    const storedUserId = sessionStorage.getItem('userid');
    setUserId(storedUserId);
  }, []);

  const handleReportChange = (e) => {
    setReportContent(e.target.value);
  };

  const handleFeedbackSubmit = async () => {
    setIsFeedbackCreating(true); // フィードバック作成を開始
    try {
      const response = await fetch('http://localhost:3000/api/report_feedback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ this_report: reportContent }),
      });

      if (response.ok) {
        const data = await response.json();
        setScores(data.score); // スコアを設定
        setSubmittedFeedback(data.feedback); // フィードバックを設定
        setPickedReports(data.picked_report); // 入力サンプルを設定
      } else {
        console.error('フィードバックの取得に失敗しました。');
      }
    } catch (error) {
      console.error('フィードバックの取得エラー:', error);
    } finally {
      setIsFeedbackCreating(false); // フィードバック作成を終了
    }
  };

  const handleReportSubmit = async () => {
    if (!userId) {
      alert('ユーザーIDが見つかりません。再度ログインしてください。');
      return;
    }

    try {
      const response = await fetch('http://localhost:3000/api/post_report', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: userId,
          report: reportContent,
        }),
      });

      if (response.ok) {
        // レポートが正常に送信された後、入力フィールドをクリア
        setReportContent('');
        alert('日報が正常に送信されました。');
      } else {
        console.error('日報の送信に失敗しました。');
        alert('日報の送信に失敗しました。');
      }
    } catch (error) {
      console.error('日報の送信エラー:', error);
      alert('日報の送信中にエラーが発生しました。');
    }
  };

  return (
    <div>
      <Header />
      {/* フィードバック作成中の警告バー */}
      {isFeedbackCreating && (
        <div className="alert-bar">
          フィードバック作成中です...
        </div>
      )}
      <div className="post-report-container">
        <div className="post-report-content">
          <div className="left-section">
            <h2>日報入力</h2>
            <div className="input-section">
              <textarea
                value={reportContent}
                onChange={handleReportChange}
                placeholder="日報を入力してください..."
              ></textarea>
            </div>

            <div className="feedback-button-section">
              <button onClick={handleFeedbackSubmit}>フィードバック確認</button>
              <button onClick={handleReportSubmit} className="create-report-button">日報作成</button>
            </div>

            <div className="score-display-section">
              <div className="score-box">内容: {scores[0]}</div>
              <div className="score-box">具体性: {scores[1]}</div>
              <div className="score-box">課題: {scores[2]}</div>
            </div>

            <div className="feedback-display-section">
              <h3>フィードバック</h3>
              <p>{submittedFeedback}</p>
            </div>
          </div>

          <div className="right-section">
            <div className="sample-report-section">
              <div className="sample-report-box" dangerouslySetInnerHTML={{ __html: `サンプル 1: ${pickedReports[0]}` }}></div>
              <div className="sample-report-box" dangerouslySetInnerHTML={{ __html: `サンプル 2: ${pickedReports[1]}` }}></div>
              <div className="sample-report-box" dangerouslySetInnerHTML={{ __html: `サンプル 3: ${pickedReports[2]}` }}></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PostReport;
