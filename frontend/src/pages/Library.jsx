import React, { useState, useEffect } from 'react';
import { ChevronRight, File, Folder, Menu, X, MessageCircle } from 'lucide-react';
import apiClient from 'config/apiConfig.js';
import SearchResultCard from 'components/SearchResultCard/SearchResultCard.jsx';
import ChatBubbleOutlineIcon from '@mui/icons-material/ChatBubbleOutline';
import { useNavigate } from 'react-router-dom';
import BackButton from 'components/BackButton.jsx';
import { useAuth } from 'context/authContext.jsx';

const Library = () => {
  const [selectedItem, setSelectedItem] = useState(null);
  const [collections, setCollections] = useState([]);
  const [loading, setLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { user } = useAuth();
  const userId = user?.user_id;
  const navigate = useNavigate();

  // Fetch collections on mount.
  useEffect(() => {
    setSelectedItem(null);
    fetchCollections();
  }, []);

  const fetchCollections = async () => {
    setLoading(true);
    try {
      const response = await apiClient.post('/getCollections', { user_id: userId });
      const collectionsData = response.data;
      setCollections(collectionsData);

      if (collectionsData.length > 0) {
        setSelectedItem({
          id: collectionsData[0].collection_id,
          type: 'folder',
          name: collectionsData[0].collection_name,
          category: 'Collections',
          papers: collectionsData[0].papers
        });
      }
    } catch (error) {
      console.error('Error fetching collections:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleNewConversation = () => {
    navigate('/chat');
  };

  const renderContent = () => {
    if (!selectedItem) {
      return (
        <div className="p-4 flex items-center justify-center h-full">
          <p className="text-gray-500 text-lg">No collections available</p>
        </div>
      );
    }

    if (selectedItem.type === 'folder' && selectedItem.papers?.length > 0) {
      return (
        <div className="p-4 w-full">
          <div className="flex justify-end mb-4">
            <button
              onClick={() => {
                console.log("Selected papers:", selectedItem.papers);
                navigate('/chat', {
                  state: selectedItem.papers.map(paper => ({
                    title: paper.title,
                    cited_by_count: paper.cited_by_count,
                    authors: paper.authors,
                    publication: paper.publication,
                    publication_year: paper.publication_year,
                    abstract: paper.abstract,
                    open_alex_id: paper.open_alex_id,
                    oa_url: paper.oa_url,
                    isPdfUrl : paper.isPdfUrl
                  }))
                });
              }}
              className="flex items-center gap-2 px-4 py-2 text-[#234869] bg-[#E5F0F9] font-['Poppins'] rounded-[30px] font-bold text-sm md:text-base"
            >
              <img src="/chat-icon.png" alt="Chat" className="h-6 w-6 " />
              <span className="hidden sm:inline">Chat with Collection</span>
              <span className="sm:hidden">Chat</span>
            </button>
          </div>
          <div className="space-y-4">
            {selectedItem.papers.map((paper) => (
              <SearchResultCard key={paper.open_alex_id} paper={paper} hideSaveButton={true} />
            ))}
          </div>
        </div>
      );
    }

    return (
      <div className="p-4 flex items-center justify-center h-full">
        <p className="text-gray-500 text-lg">No items to display</p>
      </div>
    );
  };

  // Map collections to library items.
  const getLibraryItems = () => {
    return collections.map(collection => ({
      id: collection.collection_id,
      type: 'folder',
      name: collection.collection_name,
      category: 'Collections',
      papers: collection.papers
    }));
  };

  const handleItemClick = (item) => {
    setSelectedItem(item);
    // On mobile, close the sidebar after selection
    if (window.innerWidth < 768) {
      setSidebarOpen(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col">
      <header className=" px-4">
        {/* Header with menu button for mobile */}
        <div className="flex items-center justify-between py-4">

          <button
            className="md:hidden p-2"
            onClick={() => setSidebarOpen(!sidebarOpen)}
            aria-label="Toggle sidebar"
          >
            {sidebarOpen ? <X className="h-6 w-6 text-[#234869]" /> : <Menu className="h-6 w-6 text-[#234869]" />}
          </button>
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden">
        {/* Updated Sidebar */}
        <div className={`
          fixed md:static inset-y-0 left-0 z-50
          w-4/5 max-w-[300px] md:w-64
          transform ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
          md:translate-x-0 transition-all duration-200 ease-in-out
          bg-gradient-to-b from-[#F2F5F7] to-[#F2F5F7]
          backdrop-blur-lg
          md:rounded-r-[20px]
          shadow-lg md:shadow-md
          mt-16 md:mt-0
          flex flex-col
          p-4 md:p-2
          font-['Poppins']
          overflow-x-hidden
        `}>

          {/* Collections Header */}
          <h2 className="mb-2 font-['Poppins'] text-black mt-4 text-lg font-bold">
            Collections
          </h2>

          {/* Collections List */}
          {loading ? (
            <div className="animate-pulse space-y-2">
              {[1, 2, 3].map(n => (
                <div key={n} className="h-10 bg-gray-200 rounded-lg"></div>
              ))}
            </div>
          ) : (
            <div className="space-y-1 w-full">
              {getLibraryItems().map(item => (
                <button
                  key={item.id}
                  className={`
                    w-full flex items-center gap-2 px-3 py-2
                    rounded-lg hover:bg-black/10 transition-colors
                    overflow-hidden text-left
                    ${selectedItem?.id === item.id ? "bg-black/5" : ""}
                  `}
                  onClick={() => handleItemClick(item)}
                >
                  {item.type === 'folder' ? (
                    <Folder className="h-4 w-4 flex-shrink-0 text-black" />
                  ) : (
                    <File className="h-4 w-4 flex-shrink-0 text-black" />
                  )}
                  <span
                    className={`truncate ${
                      selectedItem?.id === item.id
                        ? 'text-[16px] font-semibold'
                        : 'text-[16px] font-normal'
                    }`}
                    style={{ color: 'black', fontFamily: '"Poppins", sans-serif' }}
                  >
                    {item.name}
                  </span>
                  {item.type === 'folder' && <ChevronRight className="h-4 w-4 text-black ml-auto flex-shrink-0" />}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Overlay to close sidebar when clicked outside */}
        {sidebarOpen && (
          <div
            className="fixed inset-0 bg-black bg-opacity-50 z-40 md:hidden"
            onClick={() => setSidebarOpen(false)}
          ></div>
        )}

        {/* Main content area */}
        <div className="flex-1 overflow-auto p-0 md:p-4">
          <div className="bg-transparent min-h-screen max-w-4xl w-full mx-auto">
            {loading ? (
              <div className="p-4 space-y-4 animate-pulse">
                <div className="h-8 bg-gray-200 rounded w-1/3"></div>
                <div className="space-y-4">
                  {[1, 2, 3].map(n => (
                    <div key={n} className="h-40 bg-gray-200 rounded-lg"></div>
                  ))}
                </div>
              </div>
            ) : (
              renderContent()
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Library;
