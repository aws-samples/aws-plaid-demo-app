import * as React from 'react';
import { useState } from 'react';

import Alert from '@mui/material/Alert';
import AlertTitle from '@mui/material/AlertTitle';
import IconButton from '@mui/material/IconButton';
import Collapse from '@mui/material/Collapse';
import CloseIcon from '@mui/icons-material/Close';

export default function EmailBanner({email}) {
  const [open, setOpen] = useState(true);

  return (
      <Collapse in={open}>
        <Alert
          action={
            <IconButton
              aria-label="close"
              color="inherit"
              size="small"
              onClick={() => {
                setOpen(false);
              }}
            >
              <CloseIcon fontSize="inherit" />
            </IconButton>
          }
          sx={{ mb: 2 }}
          severity="info"
        >
        <AlertTitle>Email sent successfully!</AlertTitle>
          Please review the information sent to {email}.
        </Alert>
      </Collapse>
  );
}