import React, { useEffect, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import cartIcon from '../../images/cart.png';
import Header from '../Header/header';
import './product.css';

interface Post {
  id: number;
  post_id: string;
  username: string;
  userId: string;
  profilePic: string;
  timestamp: string;
  content: string;
  tags: string[];
  likes: number;
  replies: Reply[];
  deleted_at: string | null;
  parent_id: string | null;
}

interface Reply {
  id: number;
  username: string;
  userId: string;
  profilePic: string;
  timestamp: string;
  content: string;
}

interface ProductInfo {
  product_id: string;
  product_name: string;
  description: string;
  large_category_name: string;
  small_category: string;
}

const Product1: React.FC = () => {
  const navigate = useNavigate();
  const [posts, setPosts] = useState<Post[]>([]);
  const [filteredPosts, setFilteredPosts] = useState<Post[]>([]); // フィルタリングされた投稿を保持
  const [recommendedProducts, setRecommendedProducts] = useState<ProductInfo[]>([]);
  const [newPost, setNewPost] = useState<string>('');
  const [cartCount, setCartCount] = useState<number>(0);
  const [userTags, setUserTags] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [searchTag, setSearchTag] = useState<string>(''); // 検索タグの状態
  const [productInfo, setProductInfo] = useState<ProductInfo | null>(null);
  const [productImageUrl, setProductImageUrl] = useState<string | null>(null);
  const [repliesVisible, setRepliesVisible] = useState<{ [key: number]: boolean }>({});
  const { productId } = useParams();

  const preloadImage = (url: string) => {
    const img = new Image();
    img.src = url;
  };

  const fetchProductInfo = async () => {
    try {
      preloadImage(`http://127.0.0.1:3000/api/products/${productId}/image`);
  
      const response = await fetch(`http://127.0.0.1:3000/api/products/${productId}/info`);
      if (!response.ok) {
        throw new Error('Failed to fetch product info');
      }
      const data = await response.json();
      setProductInfo(data);
  
      const imageResponse = await fetch(`http://127.0.0.1:3000/api/products/${productId}/image`, {
        cache: 'no-cache',
      });
  
      if (imageResponse.ok) {
        const imageBlob = await imageResponse.blob();
        const imageUrl = URL.createObjectURL(imageBlob);
        console.log('Product image URL:', imageUrl);
        setProductImageUrl(imageUrl);
      } else {
        console.error('Failed to fetch product image');
      }
    } catch (error) {
      console.error('Error fetching product info:', error);
      setError('製品情報の取得に失敗しました。');
    }
  };

  const fetchProductRecommendations = async (productIds: string[]) => {
    try {
      if (productIds.length === 0) return; // productIdsが空の場合は処理を行わない
  
      const response = await fetch('http://127.0.0.1:3000/api/product_recommend', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ products_ids: productIds }),
      });
  
      if (!response.ok) {
        throw new Error('Failed to fetch product recommendations');
      }
  
      const data = await response.json();
      setRecommendedProducts(data.top_product);
    } catch (error) {
      console.error('Error fetching product recommendations:', error);
      setError('商品のおすすめ情報の取得に失敗しました。');
    }
  };
  

  const fetchProductPosts = async () => {
    try {
      const response = await fetch(`http://127.0.0.1:3000/api/product_post/${productId}`);
      if (!response.ok) {
        throw new Error('Failed to fetch product posts');
      }
      const data = await response.json();
  
      const formattedPosts = data.map((item: any, index: number) => ({
        id: index + 1,
        post_id: item.post_id,
        username: item.name,
        userId: item.user_id,
        profilePic: 'path/to/default-profile-pic.jpg',
        timestamp: new Date(item.created_at).toLocaleString(),
        content: item.material,
        tags: item.tags,
        likes: item.likes_count,
        replies: item.children.map((child: any) => ({
          id: child.post_id,
          username: child.name,
          userId: child.user_id,
          profilePic: 'path/to/default-reply-pic.jpg',
          timestamp: new Date(child.created_at).toLocaleString(),
          content: child.material,
          tags: child.tags,
        })),
        deleted_at: item.deleted_at,
        parent_id: item.parent_id,
      }));
  
      setPosts(formattedPosts);
      setFilteredPosts(formattedPosts); // 初期状態ではすべての投稿を表示
    } catch (error) {
      console.error('Error fetching product posts:', error);
      setError('投稿情報の取得に失敗しました。');
    }
  };

  const handleSearch = () => {
    if (searchTag.trim()) {
      const tags = searchTag.split(',').map(tag => tag.trim());
      const filtered = posts.filter(post =>
        tags.every(tag => post.tags.includes(tag))
      );
      setFilteredPosts(filtered);
    } else {
      setFilteredPosts(posts); // 検索タグがない場合はすべての投稿を表示
    }
  };

  const saveCommentToCSV = async (type: string, username: string, content: string, timestamp: string) => {
    try {
      const postId = "111";
      const productId = 'PRODUCT_ID';
      const userId = 'USER_ID';
      const likesCount = 0;

      const response = await fetch('http://localhost:3000/save_comment', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          post_id: postId,
          product_id: productId,
          parent_id: type === 'reply' ? String(postId) : 'NULL',
          user_id: userId,
          material: content,
          likes_count: likesCount,
          created_at: timestamp,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to save comment');
      }
      console.log('Comment saved successfully');
    } catch (error) {
      console.error('Error saving comment:', error);
    }
  };

  const handlePostSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (newPost.trim()) {
      try {
        const storedUserId = sessionStorage.getItem('userid');
        if (!storedUserId) {
          throw new Error('User ID not found in session storage');
        }

        const tags = await generateTags(newPost);

        const newPostObj: Post = {
          id: posts.length + 1,
          post_id: "generated_post_id",
          username: storedUserId,
          userId: storedUserId,
          profilePic: "path/to/profile-pic.jpg",
          timestamp: new Date().toLocaleString(),
          content: newPost,
          tags: tags,
          likes: 0,
          replies: [],
          deleted_at: null,
          parent_id: null
        };

        await saveCommentToCSV('post', newPostObj.username, newPost, newPostObj.timestamp);

        setPosts([...posts, newPostObj]);
        setNewPost('');
        handleSearch(); // 新しい投稿後も検索状態を維持する
      } catch (error) {
        console.error("投稿の送信に失敗しました:", error);
      }
    }
  };

  const handleCreateInvoice = () => {
    navigate('/invoice');
  };

  const handleLike = (postId: number) => {
    setPosts(posts.map(post =>
      post.id === postId ? { ...post, likes: post.likes + 1 } : post
    ));
  };

  const handleReplySubmit = (postId: number, e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const storedUserId = sessionStorage.getItem('userid');
    if (!storedUserId) {
      throw new Error('User ID not found in session storage');
    }
    const formData = new FormData(e.currentTarget);
    const replyContent = formData.get('reply') as string;

    const newReply: Reply = {
      id: Date.now(),
      username: storedUserId,
      userId: storedUserId,
      profilePic: "path/to/reply-profile-pic.jpg",
      timestamp: new Date().toLocaleString(),
      content: replyContent
    };

    setPosts(posts.map(post =>
      post.id === postId ? { ...post, replies: [...post.replies, newReply] } : post
    ));

    saveCommentToCSV('reply', newReply.username, replyContent, newReply.timestamp);
  };

  const toggleRepliesVisibility = (postId: number) => {
    setRepliesVisible(prevState => ({
      ...prevState,
      [postId]: !prevState[postId],
    }));
  };

  const generateTags = async (content: string): Promise<string[]> => {
    try {
      const response = await fetch('http://localhost:3000/generate_tags', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text: content }),
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      const data = await response.json();
      return Array.isArray(data.tags) ? data.tags : ["productTag_error1"];
    } catch (error) {
      console.error("タグ生成エラー:", error);
      return ["productTag_error2"];
    }
  };

  const handleAddToCart = () => {
    if (productInfo) {
      const savedCartItems = sessionStorage.getItem('cartItems');
      let cartItems = savedCartItems ? JSON.parse(savedCartItems) : [];
    
      const existingItemIndex = cartItems.findIndex((item: any) => item.id === productInfo.product_id);
    
      if (existingItemIndex > -1) {
        cartItems[existingItemIndex].count += 1;
      } else {
        cartItems.push({ id: productInfo.product_id, count: 1 });
      }
    
      sessionStorage.setItem('cartItems', JSON.stringify(cartItems));
    
      setCartCount(cartCount + 1);
    
      alert("カートに商品が追加されました!");
    }
  };

  const extractProductIds = (cartItems: string) => {
    const parsedItems = JSON.parse(cartItems);
    return parsedItems.map((item: { id: string; count: number }) => item.id);
  };
  

  useEffect(() => {
    const savedCartItems = sessionStorage.getItem('cartItems');
    fetchProductInfo();
    fetchProductPosts();

    let allProductIds = []; // allProductIds を初期化

    if (savedCartItems) {
      console.log('Saved cart items:', savedCartItems);  // Debugging log

      const cartProductIds = extractProductIds(savedCartItems);
  
      allProductIds = [...cartProductIds, productId]; // allProductIds に値を代入
    } else {
      allProductIds = [productId]; // カートに商品がない場合、productId のみを配列に格納
    }

    console.log('All product IDs:', allProductIds); // Debugging log
    console.log('Calling fetchProductRecommendations');
    fetchProductRecommendations(allProductIds); // おすすめ商品の取得を追加
  }, [productId]);
  

  return (
    <div>
      <Header />
      <div className="product1-container">
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div className="product1-image">
            {productImageUrl ? (
              <img src={productImageUrl} alt="Product" />
            ) : (
              <div className="loading-spinner">Loading...</div>
            )}
          </div>
          <button className="add-to-cart-button" onClick={handleAddToCart}>
            <img src={cartIcon} alt="Cart Icon" />
            <span className="cart-count">{cartCount}</span>
            カートに追加
          </button>
          <button className="create-invoice-button" onClick={handleCreateInvoice}>
            決済書作成
          </button>
        </div>
    
        <div className="product1-details">
          <div className="product1-column">
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
            {/*コミュニティ投稿セクション*/}
            <h2>コミュニティ投稿</h2>
            <form onSubmit={handlePostSubmit} className="product1-form">
              <textarea
                value={newPost}
                onChange={(e) => setNewPost(e.target.value)}
                placeholder="あなたの意見をシェアしてください..."
                rows={4}
              ></textarea>
              <button type="submit">投稿</button>
            </form>
            <div className="product1-posts" style={{ maxHeight: '400px', overflowY: 'scroll' }}>
              {filteredPosts.map((post) => (
                <div key={post.id} className="product1-post">
                  <div className="post-header">
                    <div className="post-info">
                      <Link to={`/profile/${post.userId}`}>
                        {post.username}
                      </Link>
                      <span>{post.timestamp}</span>
                    </div>
                  </div>
                  <p>{post.content}</p>
                  <div className="post-tags">
                    {post.tags.map((tag, index) => (
                      <span key={index} className="tag">{tag}</span>
                    ))}
                    {userTags.map((tag, index) => (
                      <span key={index} className="user_tag">{tag}</span>
                    ))}
                  </div>
                  <div className="post-actions">
                    <button onClick={() => handleLike(post.id)}>いいね ({post.likes})</button>
                  </div>

                  <div className="post-replies">
                    {post.replies.length > 0 && (
                      <>
                        <button onClick={() => toggleRepliesVisibility(post.id)}>
                          {repliesVisible[post.id] ? 'リプライを隠す' : 'リプライを見る'}
                        </button>
                        {repliesVisible[post.id] && (
                          <>
                            {post.replies.map((reply) => (
                              <div key={reply.id} className="reply">
                                <div className="reply-header">
                                  <div className="reply-info">
                                    <Link to={`/profile/${reply.userId}`}>
                                      {reply.username}
                                    </Link>
                                    <span>{reply.timestamp}</span>
                                  </div>
                                </div>
                                <p>{reply.content}</p>
                              </div>
                            ))}
                          </>
                        )}
                      </>
                    )}
                    <form onSubmit={(e) => handleReplySubmit(post.id, e)}>
                      <textarea name="reply" placeholder="リプライを入力..." rows={2}></textarea>
                      <button type="submit">リプライ</button>
                    </form>
                  </div>
                </div>
              ))}
            </div>
          </div>
    
          {productInfo && (
            <div className="product1-description">
              <h2>商品仕様</h2>
              <p>
                <strong>カテゴリー:</strong> 
                {productInfo.large_category_name} - {productInfo.small_category}
                <br />
                <strong>商品名:</strong> 
                <Link to={`/product/${productInfo.product_id}`}>
                  {productInfo.product_name}
                </Link>
              </p>
              <p><strong>説明:</strong> {productInfo.description}</p>

              {/* 横割りの枠を2つ追加 */}
              <div className="horizontal-split-container">
                <div className="horizontal-split-box">
                  <h3>同時購入商品 1</h3>
                  {recommendedProducts[0] ? (
                    <>
                      <p>
                        {recommendedProducts[0].large_category_name} - {recommendedProducts[0].small_category}
                        <br />
                        <Link to={`/product/${recommendedProducts[0].product_id}`}>
                          {recommendedProducts[0].product_name}
                        </Link>
                      </p>
                    </>
                  ) : (
                    <p>ここに仕様1の内容を入力します。</p>
                  )}
                </div>
                <div className="horizontal-split-box">
                  <h3>同時購入商品 2</h3>
                  {recommendedProducts[1] ? (
                    <>
                      <p>
                        {recommendedProducts[1].large_category_name} - {recommendedProducts[1].small_category}
                        <br />
                        <Link to={`/product/${recommendedProducts[1].product_id}`}>
                          {recommendedProducts[1].product_name}
                        </Link>
                      </p>
                    </>
                  ) : (
                    <p>ここに仕様2の内容を入力します。</p>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Product1;