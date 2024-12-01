import React from "react";
import { Box, AppBar, Toolbar, Typography } from "@mui/material";

const Layout = ({ children }) => {
  return (
    <Box
      sx={{
        minHeight: "100vh",
        backgroundColor: "background.default",
        display: "flex",
        flexDirection: "column",
      }}
    >
      <AppBar
        position="static"
        sx={{ backgroundColor: "background.paper", mb: 3 }}
      >
        <Toolbar>
          <Typography variant="h6" component="div">
            Trading Bot
          </Typography>
        </Toolbar>
      </AppBar>

      {children}
    </Box>
  );
};

export default Layout;
