import React, { useState, useCallback, useEffect } from 'react';
import {
  Typography,
  Box,
  Container,
  Paper,
  InputBase,
  IconButton,
  TextField,
  useMediaQuery,
  useTheme,
  Button,
  Stack
} from '@mui/material';
import FilterListRoundedIcon from '@mui/icons-material/FilterListRounded';
import { styled } from '@mui/material/styles';
import SearchIcon from '@mui/icons-material/Search';
import { useAuth } from 'context/authContext.jsx';
import apiClient from 'config/apiConfig.js';
import { v4 as uuidv4 } from 'uuid';
import ChatIcon from '@mui/icons-material/Chat';
import KeyboardDoubleArrowRightRoundedIcon from '@mui/icons-material/KeyboardDoubleArrowRightRounded';
import ConversationCard from 'components/ConversationCard.jsx';

const StyledTextField = styled(TextField)({
  fontFamily: '"Poppins", sans-serif',
  borderRadius: '10px',
  backgroundColor: '#FFFFFF',
  '& .MuiOutlinedInput-root': {
    borderRadius: '10px',
    '& fieldset': {
      borderColor: '#E1E9EF',
      borderRadius: '10px',
    },
  },
});

const Home = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const { loading, user } = useAuth();
  const userId = user?.user_id;
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [query, setQuery] = useState('');
  const [followUpQuery, setFollowUpQuery] = useState('');
  const [currentQuery, setCurrentQuery] = useState('');
  const [contextHistory, setContextHistory] = useState([]);
  const [currentThreadId, setCurrentThreadId] = useState(null);
  const [isInitialSearch, setIsInitialSearch] = useState(true);
  const [savedSearches, setSavedSearches] = useState([]);
  const [timeRange, setTimeRange] = useState({ from: null, to: null });
  const [journals, setJournal] = useState(null);
  const [authors, setAuthor] = useState(null);
  const [citationCount, setMinCitations] = useState(null);
  const [journalRanks, setJournalRanks] = useState([]);
  const [answer, setAnswer] = useState('');
  const [references, setReferences] = useState([]);
  const [relevantPapers, setRelevantPapers] = useState([]);
  const [resultLoading, setResultLoading] = useState(false);
  const [resultError, setResultError] = useState(null);
  const [showInitialFilters, setShowInitialFilters] = useState(true);
  const [showFollowUpFilters, setShowFollowUpFilters] = useState(false);
  const [isDeepResearch, setIsDeepResearch] = useState(false);
  const [showLogoAndTagline, setShowLogoAndTagline] = useState(true);
  const [currentFilters, setCurrentFilters] = useState({
    timeRange: { from: null, to: null },
    citationCount: null,
    authors: null,
    journals: null,
    journalRanks: []
  });

  // Extract fetchSavedSearches into a useCallback for reuse
  const fetchSavedSearches = useCallback(async () => {
    try {
      const response = await apiClient.post('/getSavedSearches', { user_id: userId });
      if (response.data) {
        const searches = Array.isArray(response.data)
          ? response.data.map((search) => ({
            searchname: search.title,
            thread_id: search.thread_id,
            searchTurns: search.saved_search,
            filters: search.filters || {
              timeRange: { from: null, to: null },
              citationCount: null,
              authors: null,
              journals: null,
              journalRanks: []
            }
          }))
          : [{
            searchname: response.data.title,
            thread_id: response.data.thread_id,
            searchTurns: response.data.saved_search,
            filters: response.data.filters || {
              timeRange: { from: null, to: null },
              citationCount: null,
              authors: null,
              journals: null,
              journalRanks: []
            }
          }];
        setSavedSearches(searches);
      } else {
        setSavedSearches([]);
      }
    } catch (err) {
      console.error('Failed to fetch saved searches', err);
      setSavedSearches([]);
    }
  }, [userId]);

  // Initial fetch of saved searches when userId changes
  useEffect(() => {
    if (userId) {
      fetchSavedSearches();
    }
  }, [userId, fetchSavedSearches]);

  // New useEffect to update sidebar after the first answer in a new thread
  useEffect(() => {
    if (answer && contextHistory.length === 0 && currentThreadId) {
      fetchSavedSearches();
    }
  }, [answer, contextHistory, currentThreadId, fetchSavedSearches]);

  useEffect(() => {
    setIsSidebarOpen(!isMobile); // Closed on mobile (true -> false), open on desktop (false -> true)
  }, [isMobile]);

  useEffect(() => {
    const savedState = JSON.parse(sessionStorage.getItem("previousPageState"));
    if (savedState?.scrollY) window.scrollTo(0, savedState.scrollY);
  }, []);

  const fetchSearchResults = useCallback(
    async (searchText, threadId) => {
      setResultLoading(true);
      setResultError(null);
      try {
        const filtersToUse = currentThreadId === threadId ? currentFilters : {
          timeRange,
          citationCount,
          authors,
          journals,
          journalRanks
        };

        const authorsList = filtersToUse.authors ? filtersToUse.authors.split(',').filter(author => author) : null;
        const journalsList = filtersToUse.journals ? filtersToUse.journals.split(',').filter(journal => journal) : null;

        const response = await apiClient.post('/askQuestion', {
          user_id: userId,
          query: searchText,
          start_year: filtersToUse.timeRange.from,
          end_year: filtersToUse.timeRange.to,
          citation_count: filtersToUse.citationCount,
          authors: authorsList,
          published_in: journalsList,
          sjr: filtersToUse.journalRanks,
          thread_id: threadId,
          is_deep_research: isDeepResearch,
          timeout: 3600000,
        });

        if (response.data.message === 'No relevant open source papers found, please update your search query and/or filters.' ||
          response.data.message === 'No query provided') {
          setResultError(response.data.message);
          setReferences([]);
          setRelevantPapers([]);
          setResultLoading(false);
          setShowLogoAndTagline(false); // Hide logo on error
          return;
        }

        if (response.status !== 200) throw new Error('Failed to fetch Answer to the question');

        setAnswer(response.data.answer);
        setReferences(response.data.references || []);
        setRelevantPapers(response.data.relevant_papers || []);
        setShowLogoAndTagline(false); // Hide logo when results arrive
      } catch (err) {
        setResultError(err.message);
        setShowLogoAndTagline(false); // Hide logo on error
      } finally {
        setResultLoading(false);
      }
    },
    [currentFilters, currentThreadId, timeRange, citationCount, authors, journals, journalRanks, userId, isDeepResearch]
  );

  const handleSearch = useCallback(
    (e) => {
      e.preventDefault();
      if (!query.trim()) return;
      const newThreadId = uuidv4();
      setCurrentThreadId(newThreadId);
      setIsInitialSearch(false);
      setContextHistory([]);
      setCurrentQuery(query);
      setQuery('');
      setAnswer('');
      setReferences([]);
      setRelevantPapers([]);
      setResultError(null);

      // Store current filters for this thread
      const currentFiltersData = {
        timeRange,
        citationCount,
        authors,
        journals,
        journalRanks
      };
      setCurrentFilters(currentFiltersData);

      fetchSearchResults(query, newThreadId);
    },
    [query, fetchSearchResults, timeRange, citationCount, authors, journals, journalRanks]
  );

  const handleFollowUpSearch = useCallback(
    (e) => {
      e.preventDefault();
      if (!followUpQuery.trim()) return;
      setContextHistory((prev) => [...prev, { query: currentQuery, answer, references, relevantPapers }]);
      setCurrentQuery(followUpQuery);
      setFollowUpQuery('');
      setAnswer('');
      setReferences([]);
      setRelevantPapers([]);
      setResultError(null);
      fetchSearchResults(followUpQuery, currentThreadId);
    },
    [followUpQuery, currentQuery, answer, references, relevantPapers, fetchSearchResults, currentThreadId]
  );

  const handleKeyPress = useCallback(
    (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSearch(e);
      }
    },
    [handleSearch]
  );

  const handleFollowUpKeyPress = useCallback(
    (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleFollowUpSearch(e);
      }
    },
    [handleFollowUpSearch]
  );

  const handleNewConversation = () => {
    setIsInitialSearch(true);
    setCurrentThreadId(null);
    setContextHistory([]);
    setCurrentQuery('');
    setAnswer('');
    setReferences([]);
    setRelevantPapers([]);
    setResultError(null);
    setQuery('');
    setFollowUpQuery('');
    setShowLogoAndTagline(true);
  };

  const loadSavedSearch = (search) => {
    setIsInitialSearch(false);
    setCurrentThreadId(search.thread_id);

    // If searchTurns has items, split them into context history and current query
    if (search.searchTurns && search.searchTurns.length > 0) {
      // Get the last item for current display
      const lastTurn = search.searchTurns[search.searchTurns.length - 1];

      // Set the previous turns as context history (excluding the last one)
      setContextHistory(search.searchTurns.slice(0, -1));

      // Set the last turn as the current query and answer
      setCurrentQuery(lastTurn.query);
      setAnswer(lastTurn.answer || '');
      setReferences(lastTurn.references || []);
      setRelevantPapers(lastTurn.relevantPapers || lastTurn.relevant_papers || []);
    } else {
      // If no turns, reset everything
      setContextHistory([]);
      setCurrentQuery('');
      setAnswer('');
      setReferences([]);
      setRelevantPapers([]);
    }

    setResultError(null);
    setShowLogoAndTagline(false);

    // Apply the filters from the saved search
    if (search.filters) {
      setTimeRange(search.filters.timeRange || { from: null, to: null });
      setMinCitations(search.filters.citationCount);
      setAuthor(search.filters.authors);
      setJournal(search.filters.journals);
      setJournalRanks(search.filters.journalRanks || []);
      setCurrentFilters(search.filters);
    }
  };

  if (loading) {
    return (
      <Box className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#234869]" />
      </Box>
    );
  }

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', margin: 0, padding: 0, width: '100%' }}>
      {/* Sidebar Toggle Button */}
      <Button
        onClick={() => setIsSidebarOpen(prev => !prev)}
        sx={{
          position: 'absolute',
          top: isMobile ? 80 : 100,
          left: isSidebarOpen ? (isMobile ? '80%' : 250) : 10,
          zIndex: 1300,
          backgroundColor: '#234869',
          color: 'white',
          borderRadius: '50%',
          minWidth: '40px',
          height: '40px',
          padding: 0,
          '&:hover': { backgroundColor: '#1a3b5c' },
          transition: 'left 0.2s ease-in-out',
        }}
      >
        <KeyboardDoubleArrowRightRoundedIcon style={{ transform: isSidebarOpen ? 'rotate(180deg)' : 'rotate(0deg)' }} />
      </Button>

      {/* Sidebar */}
      <Box
        sx={{
          width: isSidebarOpen ? (isMobile ? '80%' : 250) : 0,
          maxWidth: isMobile ? '300px' : '250px',
          p: isSidebarOpen ? (isMobile ? 2 : 1) : 0,
          fontFamily: '"Poppins", sans-serif',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'flex-start',
          textAlign: 'left',
          minHeight: '100vh',
          boxSizing: 'border-box',
          borderRadius: isSidebarOpen ? '0 20px 20px 0' : 0,
          background: 'linear-gradient(to bottom, #F2F5F7 0%, #F2F5F7 100%)',
          backdropFilter: 'blur(40px)',
          WebkitBackdropFilter: 'blur(10px)',
          boxShadow: isSidebarOpen ? '0 4px 30px rgba(0, 0, 0, 0.1)' : 'none',
          transition: 'width 0.2s ease-in-out, padding 0.2s ease-in-out, border-radius 0.2s ease-in-out',
          overflowX: 'hidden',
          position: isMobile ? 'fixed' : 'relative',
          zIndex: 1200,
        }}
      >
        {isSidebarOpen && (
          <>
            <Button
              onClick={handleNewConversation}
              sx={{
                mb: 2,
                textTransform: 'none',
                color: '#234869',
                fontFamily: '"Poppins", sans-serif',
                py: 1,
                px: 2,
                borderRadius: '30px',
                fontWeight: 'bold',
                backgroundColor: '#E1E9EF',
              }}
            >
              <ChatIcon sx={{ mr: 1, color: '#234869' }} /> New Conversation
            </Button>
            <Typography sx={{ mb: 1, fontFamily: '"Poppins", sans-serif', color: 'black', mt: 2, fontSize: '18px', fontWeight: 'bold' }}>
              Recents
            </Typography>
            {savedSearches.slice().reverse().map((search) => (
              <Button
                key={search.thread_id}
                onClick={() => loadSavedSearch(search)}
                sx={{
                  mb: 1,
                  color: currentThreadId === search.thread_id ? 'white' : 'black',
                  fontFamily: '"Poppins", sans-serif',
                  fontSize: '14px',
                  textTransform: 'none',
                  width: '100%',
                  maxWidth: 250,
                  backgroundColor: currentThreadId === search.thread_id ? '#234869' : 'transparent',
                  overflow: 'hidden',
                  display: '-webkit-box',
                  WebkitBoxOrient: 'vertical',
                  WebkitLineClamp: 1,
                  justifyContent: 'flex-start', // Left-align the text
                  textAlign: 'left',           // Ensure text is left-aligned
                  '&:hover': {
                    borderRadius: '10px',
                    backgroundColor: currentThreadId === search.thread_id ? '#234869' : 'rgba(0, 0, 0, 0.1)'
                  },
                  borderRadius: currentThreadId === search.thread_id ? '10px' : '0',
                  pl: 2, // Add left padding for better appearance
                }}
              >
                {search.searchname}
              </Button>
            ))}
          </>
        )}
      </Box>

      {/* Main Content */}
      <Box sx={{
        flex: 1,
        p: 2,
        marginLeft: isMobile && isSidebarOpen ? '80%' : 0, // Add margin when sidebar is open on mobile
        transition: 'margin-left 0.2s ease-in-out',
        width: '100%'
      }}>
        <Container maxWidth={isMobile ? 'sm' : 'md'} sx={{ pt: 2, fontFamily: '"Poppins", sans-serif', }}>
          {showLogoAndTagline && (
            <Box sx={{ textAlign: 'center', mb: 3, display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center' }}>
              <img src="/logo.png" alt="Logo" className={`md:h-40 ${isMobile ? 'max-h-[150px]' : ''}`} />
              <Typography sx={{ color: '#234869', fontSize: isMobile ? '1rem' : '1.25rem', fontFamily: '"Poppins", sans-serif', fontStyle: 'italic', mt: isMobile ? -3 : -3, mb: 4 }}>
                Accelerating research, simplifying discovery.
              </Typography>
            </Box>
          )}
          {isInitialSearch ? (
            <Box sx={{ mb: 3 }}>
              <Paper
                id="initial-search-form"
                component="form"
                sx={{
                  p: '6px 6px',
                  display: 'flex',
                  flexDirection: isMobile ? 'column' : 'row',
                  alignItems: isMobile ? 'stretch' : 'center',
                  boxShadow: 'none',
                  borderRadius: '30px',
                  backgroundColor: 'white',
                }}
                onSubmit={handleSearch}
              >
                <InputBase
                  id="initial-search-input"
                  sx={{
                    ml: isMobile ? 3 : 1,
                    flex: 1,
                    fontFamily: '"Poppins", sans-serif',
                    color: 'black',
                    fontSize: isMobile ? '14px' : '16px',
                    width: isMobile ? '100%' : 'auto',
                    mb: isMobile ? 1 : 0,
                  }}
                  multiline
                  minRows={1}
                  maxRows={8}
                  placeholder="Ask any research question"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyPress={handleKeyPress}
                />
                {/* Buttons stacked vertically on mobile */}
                <Button
                  onClick={() => setIsDeepResearch((prev) => !prev)}
                  variant="text"
                  sx={{
                    textTransform: 'none',
                    color: isDeepResearch ? 'white' : '#234869',
                    backgroundColor: isDeepResearch ? '#234869' : '#E1E9EF',
                    borderRadius: '30px',
                    padding: isMobile ? '8px 12px' : '6px 16px',
                    fontSize: isMobile ? '14px' : '16px',
                    width: isMobile ? '100%' : 'auto',
                    mb: isMobile ? 1 : 0,
                    mr: isMobile ? 0 : 1,
                  }}
                >
                  DeepResearch
                </Button>
                <Button
                  onClick={() => setShowInitialFilters((prev) => !prev)}
                  sx={{
                    width: isMobile ? '100%' : '40px',
                    backgroundColor: showInitialFilters ? '#234869' : '#E1E9EF',
                    color: showInitialFilters ? 'white' : '#234869',
                    borderRadius: '30px',
                    p: 1,
                    mb: isMobile ? 1 : 0,
                    mr: isMobile ? 0 : 1,
                  }}
                >
                  <FilterListRoundedIcon sx={{ fontSize: isMobile ? '1.5rem' : '1.25rem' }} />
                </Button>
                <IconButton
                  type="submit"
                  sx={{
                    width: isMobile ? '100%' : '40px',
                    ml: isMobile ? 0 : 1,
                  }}
                >
                  <SearchIcon sx={{ color: '#234869', fontSize: isMobile ? '1.5rem' : '1.25rem' }} />
                </IconButton>
              </Paper>
              {showInitialFilters && (
                <Paper sx={{ mt: 2, p: 2, borderRadius: '20px', backgroundColor: 'white', boxShadow: 'none' }}>
                  <Box sx={{ display: 'grid', gridTemplateColumns: isMobile ? '1fr' : '1fr 1fr', gap: isMobile ? 2 : 3 }}>
                    {/* Time Range */}
                    <Box sx={{ display: 'flex', flexDirection: isMobile ? 'column' : 'row', alignItems: isMobile ? 'flex-start' : 'center', gap: isMobile ? 1 : 4 }}>
                      <Typography sx={{ color: 'black', width: isMobile ? 'auto' : '150px', fontSize: '18px', fontFamily: '"Poppins", sans-serif', mb: isMobile ? 1 : 0 }}>
                        Time Range
                      </Typography>
                      <Box sx={{ display: 'flex', flexDirection: isMobile ? 'column' : 'row', gap: 1 }}>
                        <StyledTextField
                          id="time-range-from"
                          size="small"
                          placeholder="From"
                          value={timeRange.from}
                          onChange={(e) => setTimeRange({ ...timeRange, from: e.target.value })}
                          sx={{ width: isMobile ? '100%' : '100px', ml: isMobile ? 0 : '-48px' }}
                        />
                        <StyledTextField
                          id="time-range-to"
                          size="small"
                          placeholder="To"
                          value={timeRange.to}
                          onChange={(e) => setTimeRange({ ...timeRange, to: e.target.value })}
                          sx={{ width: isMobile ? '100%' : '100px' }}
                        />
                      </Box>
                    </Box>
                    {/* Citation Count */}
                    <Box sx={{ display: 'flex', flexDirection: isMobile ? 'column' : 'row', alignItems: isMobile ? 'flex-start' : 'center', gap: isMobile ? 1 : 0 }}>
                      <Typography sx={{ color: 'black', width: isMobile ? 'auto' : '170px', fontSize: '18px', fontFamily: '"Poppins", sans-serif', mb: isMobile ? 1 : 0 }}>
                        Citation Count
                      </Typography>
                      <StyledTextField
                        id="citation-count-input"
                        size="small"
                        placeholder="Minimum Citations"
                        value={citationCount}
                        onChange={(e) => setMinCitations(e.target.value)}
                        sx={{ width: isMobile ? '100%' : '220px', ml: isMobile ? '0px': '-20px' }}
                      />
                    </Box>
                    {/* Authors */}
                    <Box sx={{ display: 'flex', flexDirection: isMobile ? 'column' : 'row', alignItems: isMobile ? 'flex-start' : 'center', gap: isMobile ? 1 : 4, mt: isMobile ? 1 : -3 }}>
                      <Typography sx={{ color: 'black', width: isMobile ? 'auto' : '100px', fontSize: '18px', fontFamily: '"Poppins", sans-serif', }}>
                        Authors
                      </Typography>
                      <StyledTextField
                        id="authors-input"
                        size="small"
                        placeholder="Author Names"
                        value={authors}
                        onChange={(e) => setAuthor(e.target.value)}
                        sx={{ width: isMobile ? '100%' : '210px' }}
                      />
                    </Box>
                    {/* Journal Rank */}
                    <Box sx={{ display: 'flex', flexDirection: isMobile ? 'column' : 'row', alignItems: isMobile ? 'flex-start' : 'center', gap: isMobile ? 1 : 0, mt: isMobile ? 1 : 0 }}>
                      <Typography sx={{ color: 'black', width: isMobile ? 'auto' : '150px', fontSize: '18px', fontFamily: '"Poppins", sans-serif', mb: isMobile ? 1 : 0 }}>
                        Journal Rank
                      </Typography>
                      <Box sx={{ display: 'flex', gap: isMobile ? 0.5 : 1, flexWrap: 'wrap' }}>
                        {['Q1', 'Q2', 'Q3', 'Q4'].map((rank) => (
                          <Button
                            key={rank}
                            onClick={() => {
                              setJournalRanks(journalRanks.includes(rank) ? journalRanks.filter(item => item !== rank) : [...journalRanks, rank]);
                            }}
                            sx={{
                              backgroundColor: journalRanks.includes(rank) ? '#234869' : '#E1E9EF',
                              color: journalRanks.includes(rank) ? 'white':'black',
                              borderRadius: '10px',
                              border: '1px solid #E1E9EF',
                              textTransform: 'none',
                              minWidth: isMobile ? '40px' : '50px', // Smaller on mobile
                              padding: isMobile ? '2px 6px' : '6px 8px', // Smaller padding on mobile
                              fontSize: isMobile ? '12px' : 'inherit', // Smaller font on mobile
                              marginBottom: isMobile ? '4px' : 0, // Add margin bottom if buttons wrap
                              '&:hover': { backgroundColor: journalRanks.includes(rank) ? '#234869' : '#234869' },
                            }}
                          >
                            {rank}
                          </Button>
                        ))}
                      </Box>
                    </Box>
                    {/* Journals */}
                    <Box sx={{ display: 'flex', flexDirection: isMobile ? 'column' : 'row', alignItems: isMobile ? 'flex-start' : 'center', gap: isMobile ? 1 : 4, ml: isMobile ? 0 : -10, mt: isMobile ? 1 : -3 }}>
                      <Typography sx={{ color: 'black', width: isMobile ? 'auto' : '100px', fontSize: '18px', fontFamily: '"Poppins", sans-serif', marginLeft: isMobile ? 0 : 10, mb: isMobile ? 1 : 0 }}>
                        Journals
                      </Typography>
                      <StyledTextField
                        id="journals-input"
                        size="small"
                        placeholder="Journal Names"
                        value={journals}
                        onChange={(e) => setJournal(e.target.value)}
                        sx={{ width: isMobile ? '100%' : '210px' }}
                      />
                    </Box>
                  </Box>
                </Paper>
              )}
            </Box>
          ) : (
            <Box>
              <Stack spacing={7}>
                {contextHistory.map((item, index) => (
                  <ConversationCard
                    key={index}
                    query={item.query}
                    answer={item.answer}
                    references={item.references}
                    relevantPapers={item.relevant_papers}
                    loading={false}
                    error={null}
                    isDeepResearch={isDeepResearch}
                  />
                ))}
                {currentQuery && (
                  <ConversationCard
                    query={currentQuery}
                    answer={answer}
                    references={references}
                    relevantPapers={relevantPapers}
                    loading={resultLoading}
                    error={resultError}
                    isDeepResearch={isDeepResearch}
                  />
                )}
              </Stack>
              <Box sx={{ mt: 4, mb:5}}>
                <Paper
                  id="follow-up-search-form"
                  component="form"
                  sx={{
                    p: '6px 6px',
                    display: 'flex',
                    flexDirection: isMobile ? 'column' : 'row',
                    alignItems: isMobile ? 'stretch' : 'center',
                    boxShadow: 'none',
                    borderRadius: '30px',
                    backgroundColor: 'white',
                  }}
                  onSubmit={handleFollowUpSearch}
                >
                  <InputBase
                    id="follow-up-search-input"
                    sx={{
                      ml: isMobile ? 3 : 1,
                      flex: 1,
                      fontFamily: '"Poppins", sans-serif',
                      color: 'black',
                      fontSize: isMobile ? '14px' : '16px',
                      width: isMobile ? '100%' : 'auto',
                      mb: isMobile ? 1 : 0,
                    }}
                    multiline
                    minRows={1}
                    maxRows={8}
                    placeholder="Ask a follow up"
                    value={followUpQuery}
                    onChange={(e) => setFollowUpQuery(e.target.value)}
                    onKeyPress={handleFollowUpKeyPress}
                  />
                  {/* Buttons stacked vertically on mobile */}
                  <Button
                    onClick={() => setIsDeepResearch((prev) => !prev)}
                    variant="text"
                    sx={{
                      textTransform: 'none',
                      color: isDeepResearch ? 'white' : '#234869',
                      backgroundColor: isDeepResearch ? '#234869' : '#E1E9EF',
                      borderRadius: '30px',
                      padding: isMobile ? '8px 12px' : '6px 16px',
                      fontSize: isMobile ? '14px' : '16px',
                      width: isMobile ? '100%' : 'auto',
                      mb: isMobile ? 1 : 0,
                      mr: isMobile ? 0 : 1,
                    }}
                  >
                    DeepResearch
                  </Button>
                  <Button
                    onClick={() => setShowFollowUpFilters((prev) => !prev)}
                    sx={{
                      width: isMobile ? '100%' : '40px',
                      backgroundColor: showFollowUpFilters ? '#234869' : '#E1E9EF',
                      color: showFollowUpFilters ? 'white' : '#234869',
                      borderRadius: '30px',
                      p: 1,
                      mb: isMobile ? 1 : 0,
                      mr: isMobile ? 0 : 1,
                    }}
                  >
                    <FilterListRoundedIcon sx={{ fontSize: isMobile ? '1.5rem' : '1.25rem' }} />
                  </Button>
                  <IconButton
                    type="submit"
                    sx={{
                      width: isMobile ? '100%' : '40px',
                      ml: isMobile ? 0 : 1,
                    }}
                  >
                    <SearchIcon sx={{ color: '#234869', fontSize: isMobile ? '1.5rem' : '1.25rem' }} />
                  </IconButton>
                </Paper>
                {showFollowUpFilters && (
                  <Paper sx={{ mt: 2, p: 2, borderRadius: '20px', backgroundColor: 'white' }}>
                    <Box sx={{ display: 'grid', gridTemplateColumns: isMobile ? '1fr' : '1fr 1fr', gap: isMobile ? 2 : 3 }}>
                      {/* Time Range */}
                      <Box sx={{ display: 'flex', flexDirection: isMobile ? 'column' : 'row', alignItems: isMobile ? 'flex-start' : 'center', gap: isMobile ? 1 : 4 }}>
                        <Typography sx={{ color: 'black', width: isMobile ? 'auto' : '150px', fontSize: '18px', fontFamily: '"Poppins", sans-serif', mb: isMobile ? 1 : 0 }}>
                          Time Range
                        </Typography>
                        <Box sx={{ display: 'flex', flexDirection: isMobile ? 'column' : 'row', gap: 1 }}>
                          <StyledTextField
                            id="time-range-from"
                            size="small"
                            placeholder="From"
                            value={timeRange.from}
                            onChange={(e) => setTimeRange({ ...timeRange, from: e.target.value })}
                            sx={{ width: isMobile ? '100%' : '100px', ml: isMobile ? 0 : '-48px' }}
                          />
                          <StyledTextField
                            id="time-range-to"
                            size="small"
                            placeholder="To"
                            value={timeRange.to}
                            onChange={(e) => setTimeRange({ ...timeRange, to: e.target.value })}
                            sx={{ width: isMobile ? '100%' : '100px' }}
                          />
                        </Box>
                      </Box>
                      {/* Citation Count */}
                      <Box sx={{ display: 'flex', flexDirection: isMobile ? 'column' : 'row', alignItems: isMobile ? 'flex-start' : 'center', gap: isMobile ? 1 : 0 }}>
                        <Typography sx={{ color: 'black', width: isMobile ? 'auto' : '170px', fontSize: '18px', fontFamily: '"Poppins", sans-serif', mb: isMobile ? 1 : 0 }}>
                          Citation Count
                        </Typography>
                        <StyledTextField
                          id="citation-count-input"
                          size="small"
                          placeholder="Minimum Citations"
                          value={citationCount}
                          onChange={(e) => setMinCitations(e.target.value)}
                          sx={{ width: isMobile ? '100%' : '220px', ml: '-20px' }}
                        />
                      </Box>
                      {/* Authors */}
                      <Box sx={{ display: 'flex', flexDirection: isMobile ? 'column' : 'row', alignItems: isMobile ? 'flex-start' : 'center', gap: isMobile ? 1 : 4, mt: isMobile ? 1 : -3 }}>
                        <Typography sx={{ color: 'black', width: isMobile ? 'auto' : '100px', fontSize: '18px', fontFamily: '"Poppins", sans-serif', }}>
                          Authors
                        </Typography>
                        <StyledTextField
                          id="authors-input"
                          size="small"
                          placeholder="Author Names"
                          value={authors}
                          onChange={(e) => setAuthor(e.target.value)}
                          sx={{ width: isMobile ? '100%' : '210px' }}
                        />
                      </Box>
                      {/* Journal Rank */}
                      <Box sx={{ display: 'flex', flexDirection: isMobile ? 'column' : 'row', alignItems: isMobile ? 'flex-start' : 'center', gap: isMobile ? 1 : 0, mt: isMobile ? 1 : 0 }}>
                        <Typography sx={{ color: 'black', width: isMobile ? 'auto' : '150px', fontSize: '18px', fontFamily: '"Poppins", sans-serif', mb: isMobile ? 1 : 0 }}>
                          Journal Rank
                        </Typography>
                        <Box sx={{ display: 'flex', gap: isMobile ? 0.5 : 1, flexWrap: 'wrap' }}>
                          {['Q1', 'Q2', 'Q3', 'Q4'].map((rank) => (
                            <Button
                              key={rank}
                              onClick={() => {
                                setJournalRanks(journalRanks.includes(rank) ? journalRanks.filter(item => item !== rank) : [...journalRanks, rank]);
                              }}
                              sx={{
                                backgroundColor: journalRanks.includes(rank) ? '#234869' : '#E1E9EF',
                                color: journalRanks.includes(rank) ? 'white':'black',
                                borderRadius: '10px',
                                border: '1px solid #E1E9EF',
                                textTransform: 'none',
                                minWidth: isMobile ? '40px' : '50px', // Smaller on mobile
                                padding: isMobile ? '2px 6px' : '6px 8px', // Smaller padding on mobile
                                fontSize: isMobile ? '12px' : 'inherit', // Smaller font on mobile
                                marginBottom: isMobile ? '4px' : 0, // Add margin bottom if buttons wrap
                                '&:hover': { backgroundColor: journalRanks.includes(rank) ? '#234869' : '#234869' },
                              }}
                            >
                              {rank}
                            </Button>
                          ))}
                        </Box>
                      </Box>
                      {/* Journals */}
                      <Box sx={{ display: 'flex', flexDirection: isMobile ? 'column' : 'row', alignItems: isMobile ? 'flex-start' : 'center', gap: isMobile ? 1 : 4, ml: isMobile ? 0 : -10, mt: isMobile ? 1 : -3 }}>
                        <Typography sx={{ color: 'black', width: isMobile ? 'auto' : '100px', fontSize: '18px', fontFamily: '"Poppins", sans-serif', marginLeft: isMobile ? 0 : 10, mb: isMobile ? 1 : 0 }}>
                          Journals
                        </Typography>
                        <StyledTextField
                          id="journals-input"
                          size="small"
                          placeholder="Journal Names"
                          value={journals}
                          onChange={(e) => setJournal(e.target.value)}
                          sx={{ width: isMobile ? '100%' : '210px' }}
                        />
                      </Box>
                    </Box>
                  </Paper>
                )}
              </Box>
            </Box>
          )}
        </Container>
      </Box>
    </Box>
  );
};

export default Home;
