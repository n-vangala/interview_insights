import React from 'react';
import {
  Box,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Typography,
  CircularProgress,
  Alert,
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';
import { API_BASE_URL } from '../config';

interface Transcript {
  id: string;
  filename: string;
  upload_date: string;
}

interface TranscriptListProps {
  userId: string;
}

const TranscriptList: React.FC<TranscriptListProps> = ({ userId }) => {
  const queryClient = useQueryClient();

  const { data: transcripts, isLoading, error } = useQuery({
    queryKey: ['transcripts', userId],
    queryFn: async () => {
      const response = await axios.get<Transcript[]>(`${API_BASE_URL}/list/${userId}`);
      return response.data;
    },
  });

  const deleteMutation = useMutation({
    mutationFn: async (transcriptId: string) => {
      await axios.delete(`${API_BASE_URL}/delete/${transcriptId}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['transcripts', userId] });
    },
  });

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ m: 2 }}>
        Failed to load transcripts. Please try again.
      </Alert>
    );
  }

  if (!transcripts?.length) {
    return (
      <Box sx={{ p: 3, textAlign: 'center' }}>
        <Typography color="text.secondary">
          No transcripts uploaded yet.
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3, border: '1px solid #ddd', borderRadius: 1 }}>
      <Typography variant="h6" gutterBottom>
        Your Transcripts
      </Typography>

      <List>
        {transcripts.map((transcript) => (
          <ListItem
            key={transcript.id}
            divider
            sx={{
              '&:hover': {
                bgcolor: 'action.hover',
              },
            }}
          >
            <ListItemText
              primary={transcript.filename}
              secondary={new Date(transcript.upload_date).toLocaleString()}
            />
            <ListItemSecondaryAction>
              <IconButton
                edge="end"
                aria-label="delete"
                onClick={() => deleteMutation.mutate(transcript.id)}
                disabled={deleteMutation.isPending}
              >
                <DeleteIcon />
              </IconButton>
            </ListItemSecondaryAction>
          </ListItem>
        ))}
      </List>

      {deleteMutation.isError && (
        <Alert severity="error" sx={{ mt: 2 }}>
          Failed to delete transcript. Please try again.
        </Alert>
      )}
    </Box>
  );
};

export default TranscriptList; 