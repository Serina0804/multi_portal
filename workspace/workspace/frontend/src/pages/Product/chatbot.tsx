import React, { useState } from 'react';
import Draggable from 'react-draggable';
import './chatbot.css';
import botIcon from '/src/images/bot.png';

const Chatbot: React.FC = () => {
  const [messages, setMessages] = useState<{ sender: string; text: string }[]>([]);
  const [inputValue, setInputValue] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isOpen, setIsOpen] = useState<boolean>(true);  // チャットボットの開閉状態

  const handleSendMessage = async () => {
    if (inputValue.trim() !== '') {
      const userMessage = inputValue;
      setMessages([...messages, { sender: 'user', text: userMessage }]);
      setInputValue('');
      setIsLoading(true);

      try {
        const response = await fetch('http://127.0.0.1:3000/api/chatbot', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ message: userMessage }),
        });

        const data = await response.json();
        const botMessage = data.reply;
        setMessages((prevMessages) => [...prevMessages, { sender: 'bot', text: botMessage }]);
      } catch (error) {
        console.error('Error sending message:', error);
        setMessages((prevMessages) => [...prevMessages, { sender: 'bot', text: 'Error occurred while sending message' }]);
      } finally {
        setIsLoading(false);
      }
    }
  };

  const toggleChatbot = () => {
    setIsOpen(!isOpen);
  };

  return (
    <Draggable>
      <div className={`chatbot-container ${isOpen ? '' : 'closed'}`}>
        <div className="chatbot-header">
          <span>Chatbot</span>
          <button className="toggle-button" onClick={toggleChatbot}>
            {isOpen ? '−' : '＋'}
          </button>
        </div>
        {isOpen && (
          <>
            <div className="chatbot-messages">
              {messages.map((message, index) => (
                <div key={index} className={`chatbot-message ${message.sender}`}>
                  {message.sender === 'bot' && (
                    <div className="chatbot-icon">
                      <img src={botIcon} alt="bot icon" />   
                    </div>
                  )}
                  <div className="chatbot-text">
                    {message.text}
                  </div>
                </div>
              ))}
              {isLoading && (
                <div className="chatbot-message bot">
                  <div className="chatbot-icon">
                    <img src={botIcon} alt="bot icon" />
                  </div>
                  <div className="chatbot-text">
                    Bot is typing...
                  </div>
                </div>
              )}
            </div>
            <div className="chatbot-input">
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder="Type a message..."
                disabled={isLoading}
              />
              <button onClick={handleSendMessage} disabled={isLoading}>
                Send
              </button>
            </div>
          </>
        )}
      </div>
    </Draggable>
  );
};

export default Chatbot;
