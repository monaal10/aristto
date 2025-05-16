import React, { useEffect, useRef, useState } from 'react';
import PersonOutlineIcon from '@mui/icons-material/PersonOutline';
import ChatBubbleOutlineIcon from '@mui/icons-material/ChatBubbleOutline';
import FormatQuoteIcon from '@mui/icons-material/FormatQuote';
import {
  Box,
  Button,
  Typography,
  Stack,
  Tooltip,
  useMediaQuery,
  useTheme,
  IconButton,
  Menu,
  MenuItem,
} from '@mui/material';
import { useLocation, useNavigate } from 'react-router-dom';
import apiClient from 'config/apiConfig.js';
import { MenuBookOutlined, MoreVert } from '@mui/icons-material';
import { Bookmark } from 'lucide-react';
import SavePaperDialog from 'functions/SavePaperFunctions.jsx';
import LoadingContent from 'components/loading/LoadingContent.jsx';
import SearchResultCardReferences from 'components/SearchResultCard/SearchResultCardReferences.jsx'

const SearchResultCard = ({ paper, references = [], hideSaveButton }) => {
  const [activeSections, setActiveSections] = useState(new Set());
  const [sectionContents, setSectionContents] = useState({});
  const [loadingSections, setLoadingSections] = useState({});
  const [isSaved, setIsSaved] = useState(false);
  const [saveDialogOpen, setSaveDialogOpen] = useState(false);
  const [mobileMenuAnchor, setMobileMenuAnchor] = useState(null);
  const [paperInfo, setPaperInfo] = useState(null);
  const [hasFetchedPaperInfo, setHasFetchedPaperInfo] = useState(false);
  const navigate = useNavigate();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  const buttonList = [
    'Abstract',
    'Methodology',
    'Contributions',
    'Datasets',
    'Limitations',
    'Results'
  ];

  const chatWithPaper = () => {
    navigate('/chat', {
      state: {
        title: paper.title,
        cited_by_count: paper.cited_by_count,
        authors: paper.authors,
        publication: paper.publication,
        publication_year: paper.publication_year,
        open_alex_id: paper.open_alex_id,
        abstract: paper.abstract,
        oa_url: paper.oa_url,
        isPdfUrl: paper.isPdfUrl
      }
    });
  };
  const location = useLocation();
  const isOnChatPage = location.pathname === '/chat';

  const fetchPaperInfo = async () => {
    try {
      const response = await apiClient.post('/getPaperInfo', {
        paper_id: paper.open_alex_id,
        timeout: 360000
      });
      return response.data;
    } catch (err) {
      console.error('Error fetching paper info:', err);
      return null;
    }
  };

  const handleButtonClick = async (section) => {
    const newActiveSections = new Set(activeSections);

    if (newActiveSections.has(section)) {
      newActiveSections.delete(section);
      setActiveSections(newActiveSections);
      return;
    }

    newActiveSections.add(section);
    setActiveSections(newActiveSections);

    // For Abstract, just use the data already available in the paper object
    if (section === 'Abstract') {
      setSectionContents((prev) => ({
        ...prev,
        [section]: paper.abstract || 'No abstract available'
      }));
      return;
    }

    // If we already have section content, no need to fetch
    if (sectionContents[section]) return;

    // If we've already fetched paper info, use the cached data
    if (hasFetchedPaperInfo && paperInfo) {
      setSectionContents((prev) => ({
        ...prev,
        [section]: paperInfo[section.toLowerCase()] || `No ${section.toLowerCase()} available`
      }));
      return;
    }

    // First time fetching any non-Abstract section
    setLoadingSections((prev) => ({ ...prev, [section]: true }));

    try {
      const fetchedPaperInfo = await fetchPaperInfo();
      setPaperInfo(fetchedPaperInfo);
      setHasFetchedPaperInfo(true);

      if (fetchedPaperInfo) {
        // Update all section contents at once, even ones not clicked yet
        const newSectionContents = { ...sectionContents };

        buttonList.forEach((buttonSection) => {
          if (buttonSection !== 'Abstract') {
            const key = buttonSection.toLowerCase();
            newSectionContents[buttonSection] =
              fetchedPaperInfo[key] || `No ${key} available`;
          }
        });

        setSectionContents(newSectionContents);
      }
    } catch (error) {
      console.error(`Error loading paper info:`, error);
      setSectionContents((prev) => ({
        ...prev,
        [section]: `Error loading ${section.toLowerCase()}`
      }));
    } finally {
      setLoadingSections((prev) => ({ ...prev, [section]: false }));
    }
  };

  const handleSaveClick = (e) => {
    e.stopPropagation();
    setSaveDialogOpen(true);
    // Removed the setIsSaved(true) line from here
  };

  // New callback function to handle successful save
  const handleSaveSuccess = () => {
    setIsSaved(true);
  };

  const handleOpenMobileMenu = (event) => {
    setMobileMenuAnchor(event.currentTarget);
  };

  const handleCloseMobileMenu = () => {
    setMobileMenuAnchor(null);
  };

  return (
    <Box
      sx={{
        bgcolor: 'transparent',
        width: '100%',
        maxWidth: '100%',
        mb: 4,
        p: { xs: 1, md: 0.5 },
        position: 'relative',
        overflow: 'hidden',
        borderRadius: '10px',
        borderColor: '#B39984'
      }}
    >
      {/* Header Section - Title and Reference Numbers */}
      <Box sx={{
        display: 'flex',
        flexDirection: { xs: 'column', sm: 'row' },
        alignItems: { xs: 'flex-start', sm: 'flex-start' },
        width: '100%',
        mb: { xs: 1, sm: 0 }
      }}>
        <Box sx={{
          display: 'flex',
          flexDirection: 'row',
          alignItems: 'flex-start',
          width: '100%'
        }}>
          {references.length > 0 && (
            <Typography
              variant="h5"
              sx={{
                fontWeight: 'bold',
                color: 'text.primary',
                fontSize: '1rem',
                mr: 1,
                flexShrink: 0
              }}
            >
              [{references.map(ref => ref.number).sort((a, b) => a - b).join(', ')}]
            </Typography>
          )}
          <Typography
            variant="h5"
            sx={{
              fontWeight: 'bold',
              color: 'text.primary',
              fontSize: '1rem',
              wordBreak: 'break-word',
              width: '100%',
              mr: { xs: 0, sm: 2 }
            }}
          >
            {paper.title}
          </Typography>
        </Box>

        <Box sx={{
          display: 'flex',
          alignItems: 'center',
          flexShrink: 0,
          mt: { xs: 1, sm: 0 },
          ml: { xs: 0, sm: 'auto' },
          width: { xs: '100%', sm: 'auto' },
          justifyContent: { xs: 'space-between', sm: 'flex-end' }
        }}>
          {paper.oa_url && (
            <a
              href={paper.oa_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 hover:text-blue-800 underline mr-2 text-sm"
            >
              Open Paper
            </a>
          )}
          <Typography sx={{
            color: '#000000',
            display: 'flex',
            alignItems: 'center',
          }}>
            <FormatQuoteIcon fontSize="small" />
            <Typography
              component="span"
              sx={{ fontWeight: 'bold', textDecoration: 'underline', mx: 0.5 }}
            >
              {paper.cited_by_count}
            </Typography>
            <Box sx={{ mx: 1 }}>{paper.publication_year}</Box>
          </Typography>
        </Box>
      </Box>

      {/* Authors */}
      <Typography
        sx={{
          display: 'flex',
          alignItems: 'flex-start',
          fontFamily: '"Poppins", sans-serif',
          fontStyle: 'italic',
          fontWeight: 300,
          fontSize: { xs: 14, md: 16 },
          mt: 1,
          flexWrap: 'wrap',
        }}
      >
        <PersonOutlineIcon sx={{ mr: 1, flexShrink: 0 }} />
        <span style={{ wordBreak: 'break-word' }}>
          {paper.authors ? paper.authors.join(', ') : 'No authors listed'}
        </span>
      </Typography>

      {/* Publication */}
      <Box sx={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        width: '100%',
        mt: 1
      }}>
        <Typography
          sx={{
            display: 'flex',
            alignItems: 'center',
            fontStyle: 'italic',
            fontWeight: 300,
            fontSize: { xs: 12, md: 14 },
            flexWrap: 'wrap',
            flexGrow: 1,
            maxWidth: 'calc(100% - 80px)',
            ml: 0.5
          }}
        >
          <MenuBookOutlined sx={{ mr: 1, flexShrink: 0, fontSize: 'small' }} />
          <span style={{ wordBreak: 'break-word' }}>
            {paper.publication || 'No venue information'}
          </span>
        </Typography>
      </Box>

      {/* Reference Texts */}
      {references && <SearchResultCardReferences references={references} />}

      {/* Section Buttons and Action Buttons */}
      <Box sx={{
        position: 'relative',
        mt: 1,
        ml: { xs: 0, sm: -2 },
        overflowX: 'auto',
        width: '100%'
      }}>
        {isMobile ? (
          <Stack
            direction="row"
            sx={{
              justifyContent: 'space-between',
              alignItems: 'center',
              width: '100%',
              mt: 1
            }}
          >
            {paper.isPdfUrl === true && paper.oa_url && (
              <Box sx={{ display: 'flex', overflowX: 'auto', pb: 1, width: 'calc(100% - 60px)' }}>
                {buttonList.map((label) => (
                  <Button
                    key={label}
                    onClick={() => handleButtonClick(label)}
                    sx={{
                      mr: 1,
                      borderRadius: 5,
                      textTransform: 'none',
                      px: { xs: 1, sm: 2 },
                      py: 0.5,
                      fontSize: { xs: '0.75rem', sm: '0.875rem' },
                      bgcolor: activeSections.has(label) ? '#234869' : 'white',
                      color: activeSections.has(label) ? 'white' : '#234869',
                      '&:hover': {
                        color: activeSections.has(label) ? 'black' : '#234869'
                      },
                      whiteSpace: 'nowrap',
                      minWidth: 'auto',
                      flexShrink: 0
                    }}
                  >
                    {label}
                  </Button>
                ))}
              </Box>
            )}
            <Box>
              <IconButton
                onClick={handleOpenMobileMenu}
                size="small"
                sx={{ ml: 'auto' }}
              >
                <MoreVert />
              </IconButton>
              <Menu
                anchorEl={mobileMenuAnchor}
                open={Boolean(mobileMenuAnchor)}
                onClose={handleCloseMobileMenu}
              >
                {hideSaveButton !== true && (
                  <MenuItem onClick={(e) => {
                    handleSaveClick(e);
                    handleCloseMobileMenu();
                  }}>
                    <Bookmark
                      size={16}
                      className={isSaved ? 'fill-current' : ''}
                      sx={{ mr: 1 }}
                    />
                    Save paper
                  </MenuItem>
                )}
                {paper.isPdfUrl === true &&paper.oa_url && !isOnChatPage && (
                  <MenuItem onClick={() => {
                    chatWithPaper()
                    handleCloseMobileMenu()
                  }}>
                    <img src="/chat-icon.png" alt="Chat" className="h-5 w-5 " />
                    Chat with paper
                  </MenuItem>
                )}
              </Menu>
            </Box>
          </Stack>
        ) : (
          <Stack
            direction="row"
            sx={{
              justifyContent: 'space-between',
              alignItems: 'center',
              p: 0,
              width: '100%',
              pb: { xs: 1, md: 0 },
              mt: 1
            }}
          >
            <Box sx={{
              display: 'flex',
              flexWrap: { xs: 'nowrap', md: 'wrap' },
              gap: 1,
              flexGrow: 1
            }}>
              {paper.isPdfUrl === true && paper.oa_url && buttonList.map((label) => (
                <Button
                  key={label}
                  onClick={() => handleButtonClick(label)}
                  sx={{
                    ml: 2,
                    borderRadius: 5,
                    textTransform: 'none',
                    px: 2,
                    bgcolor: activeSections.has(label) ? '#234869' : 'white',
                    color: activeSections.has(label) ? 'white' : '#234869',
                    '&:hover': {
                      color: activeSections.has(label) ? 'black' : '#234869'
                    },
                    whiteSpace: 'nowrap',
                    minWidth: 'auto',
                  }}
                >
                  {label}
                </Button>
              ))}
              {paper.isPdfUrl === false && !paper.oa_url && <Box sx={{ flexGrow: 1 }} />}
            </Box>
            <Box sx={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'flex-end',
              flexShrink: 0,
              ml: 'auto',
              mr: 2
            }}>
              {hideSaveButton !== true && (
                <Tooltip title="save paper">
                  <Button
                    onClick={handleSaveClick}
                    variant="contained"
                    sx={{
                      color: '#234869',
                      borderRadius: 3,
                      textTransform: 'none',
                      fontFamily: '"Poppins", sans-serif',
                      bgcolor: 'transparent',
                      boxShadow: 'none',
                      minWidth: 'auto',
                      padding: '2px',
                      '&:hover': {
                        bgcolor: 'transparent',
                      }
                    }}
                  >
                    <Bookmark
                      size={20}
                      className={isSaved ? 'fill-current' : ''}
                      style={{ fill: isSaved ? '#234869' : 'none' }}
                    />
                  </Button>
                </Tooltip>
              )}
              {paper.isPdfUrl === true && paper.oa_url && !isOnChatPage && (
                <Tooltip title="chat with paper">
                  <Button
                    onClick={chatWithPaper}
                    variant="contained"
                    sx={{
                      color: '#234869',
                      borderRadius: 3,
                      textTransform: 'none',
                      fontFamily: '"Poppins", sans-serif',
                      bgcolor: 'transparent',
                      boxShadow: 'none',
                      minWidth: 'auto',
                      padding: '2px',
                      ml: 1,
                      '&:hover': {
                        bgcolor: 'transparent',
                      }
                    }}
                  >
                    <img src="/chat-icon.png" alt="Chat" className="h-5 w-5 " />
                  </Button>
                </Tooltip>
              )}
            </Box>
          </Stack>
        )}
        <SavePaperDialog
          open={saveDialogOpen}
          onClose={() => setSaveDialogOpen(false)}
          paperId={paper.open_alex_id}
          onSaveSuccess={handleSaveSuccess}
        />
      </Box>

      {/* Display active sections */}
      {Array.from(activeSections).map((section) => (
        <Box key={section} sx={{ mt: 2 }}>
          <Typography
            variant="h6"
            sx={{
              color: 'black',
              fontFamily: 'Noto Sans',
              fontWeight: 'regular',
              fontSize: { xs: 18, md: 20 },
              mb: 1
            }}
          >
            {section}
          </Typography>
          {loadingSections[section] ? (
            <LoadingContent />
          ) : (
            <Typography
              variant="body2"
              sx={{
                wordBreak: 'break-word',
                whiteSpace: 'pre-wrap'
              }}
            >
              {sectionContents[section]}
            </Typography>
          )}
        </Box>
      ))}
    </Box>
  );
};

export default SearchResultCard;
