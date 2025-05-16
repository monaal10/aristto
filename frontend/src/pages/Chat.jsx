import { useLocation } from 'react-router-dom';
import React, { useEffect, useState } from 'react';
import { LoadingContent } from 'components/loading/LoadingContent.jsx';
import apiClient from 'config/apiConfig.js';
import SearchResultCard from 'components/SearchResultCard/SearchResultCard.jsx';
import { Send, Menu } from 'lucide-react';

const Chat = () => {
  const location = useLocation();
  const [papers, setPapers] = useState([]);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [inputMessage, setInputMessage] = useState('');
  const [showPapers, setShowPapers] = useState(false);

  useEffect(() => {
    if (location.state) {
      const newPapers = Array.isArray(location.state) ? location.state : [location.state];

      setPapers(prev => {
        // Filter out duplicates based on open_alex_id
        const uniquePapers = newPapers.filter(newPaper =>
          !prev.some(p => p.open_alex_id === newPaper.open_alex_id)
        );
        return [...prev, ...uniquePapers];
      });
    }

    const savedMessages = localStorage.getItem('chatMessages');
    if (savedMessages) {
      setMessages(JSON.parse(savedMessages));
    }

    // Set initial visibility based on screen size
    setShowPapers(window.innerWidth >= 768);

    // Clear chatMessages on page unload
    const handleUnload = () => {
      localStorage.removeItem('chatMessages');
    };

    const handleResize = () => {
      if (window.innerWidth >= 768) {
        setShowPapers(true);
      }
    };

    window.addEventListener('beforeunload', handleUnload);
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('beforeunload', handleUnload);
      window.removeEventListener('resize', handleResize);
      localStorage.removeItem('chatMessages'); // Clear on component unmount
    };
  }, [location.state]);

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;

    setLoading(true);
    const userMessage = {
      human_message: inputMessage
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');

    try {
      const response = await apiClient.post('/chatWithPapers', {
        query: inputMessage,
        paper_ids: papers?.map(paper => paper.open_alex_id) || [],
        conversation_history: localStorage.getItem('chatMessages')
          ? JSON.parse(localStorage.getItem('chatMessages'))
          : [],
      });

      const assistantMessage = {
        assistant_message: response.data.answer
      };

      setMessages(prev => {
        const updatedMessages = [...prev, assistantMessage];
        localStorage.setItem('chatMessages', JSON.stringify(updatedMessages));
        return updatedMessages;
      });
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        assistant_message: "Sorry, there was an error processing your message."
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const togglePapers = () => {
    setShowPapers(!showPapers);
  };

  return (
    <div className="flex flex-col md:flex-row h-screen">
      {/* Toggle Papers Button (Mobile only) */}
      <div className="md:hidden fixed top-20 left-3 z-20">
        <button
          onClick={togglePapers}
          className="p-2 rounded-full bg-white shadow-sm"
        >
          <Menu size={24} />
        </button>
      </div>

      {/* Left panel - Papers using SearchResultCard */}
      <div
        className={`${
          showPapers ? 'block' : 'hidden'
        } md:block w-full md:w-5/12 px-4 md:pl-12 md:pr-0 py-6 overflow-y-auto mt-8 md:static ${
          showPapers && 'fixed inset-0 z-10 bg-white'
        }`}
      >
        {papers.map((paper, index) => (
          <SearchResultCard key={index} paper={paper} hideSaveButton={false} />
        ))}

        {/* Close button for mobile */}
        {showPapers && (
          <div className="md:hidden fixed top-4 right-4">
            <button
              onClick={togglePapers}
              className="p-2 rounded-full bg-gray-100"
            >
              &times;
            </button>
          </div>
        )}
      </div>

      {/* Spacer - only on desktop */}
      <div className="hidden md:block md:w-1/12" />

      {/* Right panel - Chat */}
      <div className="w-full md:w-5/12 py-6 flex flex-col h-[80vh] md:h-[80vh] rounded-[10px]" style={{ backgroundColor: '#E1E9EF' }}>
        {/* Messages area */}
        <div
          className="flex-1 overflow-y-auto mb-4 px-4 md:px-6"
          style={{ maxHeight: 'calc(100vh - 150px)' }}
        >
          {loading ? (<div className="invert brightness-0">
              <LoadingContent /> </div>
          ) : (
            messages.map((msg, index) => (
              <div key={index} className="mb-4">
                {msg.assistant_message && (
                  <div className="flex justify-start mb-2">
                    <div className="bg-white rounded-lg p-3 max-w-[90%] md:max-w-[80%] shadow-sm">
                      {msg.assistant_message}
                    </div>
                  </div>
                )}
                {msg.human_message && (
                  <div className="flex justify-end mb-2">
                    <div className="bg-white rounded-lg p-3 max-w-[90%] md:max-w-[80%] shadow-sm">
                      {msg.human_message}
                    </div>
                  </div>
                )}
              </div>
            ))
          )}
        </div>

        {/* Input area */}
        <div className="flex items-center gap-2 px-4 md:px-6">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
            className="flex-1 p-3 bg-[#F8F5F0] rounded-3xl shadow-sm"
            placeholder="Type your message..."
            disabled={loading}
          />
          <button
            onClick={handleSendMessage}
            disabled={loading}
            className="p-3 rounded-full bg-[#F8F5F0] shadow-sm hover:bg-gray-50 disabled:opacity-50"
          >
            <Send size={20} className="text-gray-600" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default Chat;
