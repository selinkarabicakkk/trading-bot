import React from "react";
import {
  ThemeProvider,
  createTheme,
  StyledEngineProvider,
} from "@mui/material/styles";
import CssBaseline from "@mui/material/CssBaseline";
import Dashboard from "./components/Dashboard";

const darkTheme = createTheme({
  palette: {
    mode: "dark",
    primary: {
      main: "#1a237e",
    },
    secondary: {
      main: "#4caf50",
    },
    background: {
      default: "#121212",
      paper: "#1e1e1e",
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: "none",
        },
      },
    },
  },
});

function App() {
  return (
    <StyledEngineProvider injectFirst>
      <ThemeProvider theme={darkTheme}>
        <CssBaseline />
        <Dashboard />
      </ThemeProvider>
    </StyledEngineProvider>
  );
}

export default App;
