import React, { useState } from 'react'
import { useAuth } from 'context/authContext.jsx'
import apiClient from 'config/apiConfig.js'
import {
  Box, Button,
  Dialog, DialogActions,
  DialogContent,
  DialogTitle,
  List,
  ListItem,
  ListItemButton, ListItemText,
  Tab,
  Tabs, TextField,
  Typography,
  Paper,
  CircularProgress
} from '@mui/material'
import { Bookmark } from 'lucide-react';

const SavePaperDialog = ({ open, onClose, paperId, onSaveSuccess }) => {
  const [tab, setTab] = useState(0);
  const [collections, setCollections] = useState([]);
  const [newCollectionName, setNewCollectionName] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const { user } = useAuth();
  const userId = user?.user_id;

  const handleTabChange = (event, newValue) => {
    setTab(newValue);
    setMessage('');
  };

  const handleSaveToCollection = async (collectionName, collectionId = null) => {
    setLoading(true);
    try {
      await apiClient.post('/savePapers', {
        collection_name: collectionName,
        collection_id: collectionId,
        user_id: userId,
        paper_id: paperId
      });

      setMessage('Paper saved to collection');

      // Call the onSaveSuccess callback to update parent component
      if (onSaveSuccess) {
        onSaveSuccess();
      }

      setTimeout(() => {
        onClose();
      }, 1500);
    } catch (error) {
      console.error('Error saving paper:', error);
      setMessage('Error saving paper');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveToNewCollection = async () => {
    if (!newCollectionName.trim()) {
      setMessage('Please enter a collection name');
      return;
    }
    await handleSaveToCollection(newCollectionName);
  };

  // Fetch existing collections when dialog opens
  React.useEffect(() => {
    if (open && userId) {
      fetchCollections();
    }
  }, [open, userId]);

  const fetchCollections = async () => {
    setLoading(true);
    try {
      const response = await apiClient.post('/getCollections', {
        user_id: userId
      });
      const collectionsData = Array.isArray(response.data)
        ? response.data
        : typeof response.data === 'string'
          ? JSON.parse(response.data)
          : [];
      setCollections(collectionsData);
    } catch (error) {
      console.error('Error fetching collections:', error);
      setMessage('Error loading collections');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="sm"
      fullWidth
      PaperProps={{
        sx: {
          borderRadius: '10px',
          boxShadow: '0px 4px 20px rgba(0, 0, 0, 0.1)',
        }
      }}
    >
      <DialogTitle sx={{
        fontFamily: '"Poppins", sans-serif',
        fontSize: '1.25rem',
        fontWeight: 600,
        color: '#234869',
        paddingBottom: 1
      }}>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <Bookmark size={20} style={{ marginRight: '10px' }} />
          Save Paper
        </Box>
      </DialogTitle>

      <DialogContent sx={{ paddingTop: '8px !important' }}>
        <Tabs
          value={tab}
          onChange={handleTabChange}
          sx={{
            mb: 2,
            '& .MuiTabs-indicator': {
              backgroundColor: '#234869',
            },
            '& .MuiTab-root': {
              fontFamily: '"Poppins", sans-serif',
              textTransform: 'none',
              '&.Mui-selected': {
                color: '#234869',
                fontWeight: 600
              }
            }
          }}
        >
          <Tab label="Existing Collections" />
          <Tab label="New Collection" />
        </Tabs>

        {message && (
          <Paper
            elevation={0}
            sx={{
              p: 1.5,
              mb: 2,
              bgcolor: message.includes('Error') ? '#FFEBEE' : '#E8F5E9',
              borderRadius: '8px'
            }}
          >
            <Typography
              color={message.includes('Error') ? 'error' : 'success'}
              sx={{
                fontFamily: '"Poppins", sans-serif',
                fontSize: '0.875rem'
              }}
            >
              {message}
            </Typography>
          </Paper>
        )}

        {tab === 0 && (
          <>
            {loading && collections.length === 0 ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
                <CircularProgress size={32} sx={{ color: '#234869' }} />
              </Box>
            ) : (
              <List sx={{
                maxHeight: '300px',
                overflow: 'auto',
                p: 0,
                '& .MuiListItemButton-root:hover': {
                  bgcolor: 'rgba(35, 72, 105, 0.08)',
                }
              }}>
                {collections && collections.length > 0 ? (
                  collections.map((collection) => (
                    <ListItem key={collection.collection_id} disablePadding>
                      <ListItemButton
                        onClick={() =>
                          handleSaveToCollection(
                            collection.collection_name,
                            collection.collection_id
                          )
                        }
                        disabled={loading}
                        sx={{
                          borderRadius: '8px',
                          my: 0.5,
                          p: 1.5
                        }}
                      >
                        <ListItemText
                          primary={collection.collection_name}
                          primaryTypographyProps={{
                            fontFamily: '"Poppins", sans-serif',
                            fontWeight: 500
                          }}
                        />
                      </ListItemButton>
                    </ListItem>
                  ))
                ) : (
                  <ListItem sx={{ py: 2 }}>
                    <ListItemText
                      primary="No collections found"
                      primaryTypographyProps={{
                        fontFamily: '"Poppins", sans-serif',
                        fontStyle: 'italic',
                        textAlign: 'center',
                        color: 'text.secondary'
                      }}
                    />
                  </ListItem>
                )}
              </List>
            )}
          </>
        )}

        {tab === 1 && (
          <Box sx={{ mt: 2 }}>
            <TextField
              fullWidth
              label="Collection Name"
              value={newCollectionName}
              onChange={(e) => setNewCollectionName(e.target.value)}
              disabled={loading}
              variant="outlined"
              sx={{
                '& .MuiOutlinedInput-root': {
                  borderRadius: '8px',
                  '&.Mui-focused fieldset': {
                    borderColor: '#234869',
                  },
                },
                '& .MuiInputLabel-root.Mui-focused': {
                  color: '#234869',
                },
              }}
              InputProps={{
                sx: { fontFamily: '"Poppins", sans-serif' }
              }}
              InputLabelProps={{
                sx: { fontFamily: '"Poppins", sans-serif' }
              }}
            />
          </Box>
        )}
      </DialogContent>

      <DialogActions sx={{
        p: '16px 24px',
        display: 'flex',
        justifyContent: 'space-between'
      }}>
        <Button
          onClick={onClose}
          disabled={loading}
          sx={{
            color: '#234869',
            textTransform: 'none',
            fontFamily: '"Poppins", sans-serif',
            '&:hover': {
              backgroundColor: 'rgba(35, 72, 105, 0.08)',
            }
          }}
        >
          Cancel
        </Button>

        {tab === 1 && (
          <Button
            onClick={handleSaveToNewCollection}
            disabled={loading || !newCollectionName.trim()}
            variant="contained"
            sx={{
              bgcolor: '#234869',
              color: 'white',
              textTransform: 'none',
              borderRadius: '8px',
              fontFamily: '"Poppins", sans-serif',
              boxShadow: 'none',
              '&:hover': {
                bgcolor: '#1a3a57',
                boxShadow: 'none',
              },
              '&.Mui-disabled': {
                bgcolor: 'rgba(35, 72, 105, 0.38)',
                color: 'white',
              }
            }}
            startIcon={loading ? <CircularProgress size={16} color="inherit" /> : null}
          >
            {loading ? 'Saving...' : 'Create & Save'}
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default SavePaperDialog;
