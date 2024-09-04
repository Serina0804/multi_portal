import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import Header from '../Header/header';
import './profile.css';

const ProfileComponent: React.FC = () => {
  const { userId } = useParams();
  const navigate = useNavigate();
  const [profileData, setProfileData] = useState<any>(null);
  const [reviews, setReviews] = useState<any[]>([]);
  const [reports, setReports] = useState<any[]>([]);
  const [filteredReviews, setFilteredReviews] = useState<any[]>([]);
  const [searchTag, setSearchTag] = useState<string>('');
  const [isReviewsOpen, setIsReviewsOpen] = useState(false);
  const [isReportsOpen, setIsReportsOpen] = useState(false);

  useEffect(() => {
    const fetchProfileData = async () => {
      try {
        const response = await fetch(`http://localhost:3000/api/profile/${userId}`);
        if (response.ok) {
          const data = await response.json();
          setProfileData(data);
        } else {
          console.error("プロフィールデータの取得に失敗しました");
        }
      } catch (error) {
        console.error('プロフィールデータの取得に失敗しました:', error);
      }
    };

    const fetchReviews = async (tags: string[] = []) => {
      try {
        let url = `http://localhost:3000/api/profile_post/${userId}`;
        if (tags.length > 0) {
          url += `?tags=${tags.join(',')}`;
        }
        const response = await fetch(url);
        if (response.ok) {
          const data = await response.json();
          setReviews(data);
          setFilteredReviews(data); // フィルタリング後の結果を保存
        } else {
          console.error("レビュー投稿の取得に失敗しました");
        }
      } catch (error) {
        console.error('レビュー投稿の取得に失敗しました:', error);
      }
    };

    const fetchReports = async () => {
      try {
        const response = await fetch(`http://localhost:3000/api/reports_with_tags/${userId}`);
        if (response.ok) {
          const data = await response.json();
          setReports(data);
        } else {
          console.error("日報の取得に失敗しました");
        }
      } catch (error) {
        console.error('日報の取得に失敗しました:', error);
      }
    };

    if (userId) {
      fetchProfileData();
      fetchReviews(); // 初期ロード時はすべてのレビューを表示
      fetchReports(); // 日報の取得を追加
    }
  }, [userId]);

  const handleSearch = () => {
    const tags = searchTag.split(',').map(tag => tag.trim()).filter(tag => tag !== '');
    if (tags.length > 0) {
      setFilteredReviews(reviews.filter(review => tags.every(tag => review.tags.includes(tag))));
    } else {
      setFilteredReviews(reviews);
    }
  };

  const handleCreateReport = () => {
    navigate('/report'); // /reportに遷移
  };

  if (!profileData) {
    return <div>Loading...</div>;
  }

  const reviewsToShow = isReviewsOpen ? filteredReviews : filteredReviews.slice(0, 3);
  const reportsToShow = isReportsOpen ? reports : reports.slice(0, 3);

  return (
    <div>
      <Header />
      <div className="profile-container">
        <div className="profile-header">
          <div className="profile-text">
            <h2 className="profile-name">{profileData.name}</h2>
            <p className="profile-gender">性別: {profileData.gender || "未設定"}</p>
            <p className="profile-occupation">職種: {profileData.occupation}</p>
            <p className="profile-email">メールアドレス: {profileData.email}</p>
          </div>
          <div className="profile-bio">
            <h3>経歴</h3>
            <p>{profileData.profile}</p>
          </div>
        </div>

        <div className="profile-content">
          <div className="left-section">
            {/* 検索セクション */}
            <div className="search-bar">
              <input
                type="text"
                placeholder="タグで検索（カンマ区切りで複数指定可）"
                value={searchTag}
                onChange={(e) => setSearchTag(e.target.value)}
              />
              <button onClick={handleSearch}>検索</button>
            </div>

            {/* レビューセクション */}
            <div className="reviews">
              <h3 onClick={() => setIsReviewsOpen(!isReviewsOpen)} style={{ cursor: 'pointer' }}>
                レビュー投稿 {isReviewsOpen ? '▲' : '▼'}
              </h3>
              <ul>
                {reviewsToShow.map((review: any, index: number) => (
                  <li key={index}>
                    {/* 商品名を追加 */}
                    <p>
                      <strong>{review.large_category_name} - {review.small_category} - </strong>
                      <Link to={`/product/${review.product_id}`}>
                        {review.product_name}
                      </Link>
                    </p>
                    <p>{review.material}</p>
                    <small>いいね👍: {review.likes_count}</small>
                    <div className="tags">
                      {review.tags.map((tag: string, tagIndex: number) => (
                        <span key={tagIndex} className="tag">{tag}</span>
                      ))}
                    </div>
                  </li>
                ))}
              </ul>
              {!isReviewsOpen && filteredReviews.length > 3 && (
                <p onClick={() => setIsReviewsOpen(true)} style={{ cursor: 'pointer', color: 'blue' }}>
                  もっと見る ▼
                </p>
              )}
            </div>
          </div>

          <div className="right-section">
            {/* 日報作成ボタン */}
            <div className="create-report-button" onClick={handleCreateReport}>
              日報を作成
            </div>

            {/* 日報セクション */}
            <div className="reports">
              <h3 onClick={() => setIsReportsOpen(!isReportsOpen)} style={{ cursor: 'pointer' }}>
                日報一覧 {isReportsOpen ? '▲' : '▼'}
              </h3>
              <ul>
                {reportsToShow.map((report: any, index: number) => (
                  <li key={index} style={{ marginBottom: '20px' }}>
                    <p style={{ whiteSpace: 'pre-wrap', margin: 0 }}>{report.material}</p>
                    <div className="tags">
                      {report.tags && report.tags.map((tag: string, tagIndex: number) => (
                        <span key={tagIndex} className="tag">{tag}</span>
                      ))}
                    </div>
                    <small style={{ display: 'block', marginTop: '5px' }}>更新日: {report.updated_at}</small>
                  </li>
                ))}
              </ul>
              {!isReportsOpen && reports.length > 3 && (
                <p onClick={() => setIsReportsOpen(true)} style={{ cursor: 'pointer', color: 'blue' }}>
                  もっと見る ▼
                </p>
              )}
            </div>
          </div>
        </div>

        {/* カレンダーセクション */}
        <div className="calendar">
          <h3>カレンダー</h3>
          <iframe
            src="https://calendar.google.com/calendar/embed?src=ja.malaysia%23holiday%40group.v.calendar.google.com&ctz=Asia%2FTokyo"
            style={{ border: 0 }}
            width="800"
            height="600"
            frameBorder="0"
            scrolling="no"
          ></iframe>
        </div>
      </div>
    </div>
  );
};

export default ProfileComponent;
