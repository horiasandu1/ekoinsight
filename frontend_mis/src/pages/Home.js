
import { Link } from "react-router-dom";

import * as React from "react";
import { useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";

import Avatar from "@mui/material/Avatar";
import Button from "@mui/material/Button";
import CssBaseline from "@mui/material/CssBaseline";
import Box from "@mui/material/Box";
import LockOutlinedIcon from "@mui/icons-material/LockOutlined";
import Typography from "@mui/material/Typography";
import Container from "@mui/material/Container";
import { createTheme, ThemeProvider } from "@mui/material/styles";

import { GoogleLogin, useGoogleLogin, googleLogout, hasGrantedAllScopesGoogle } from "@react-oauth/google";

const defaultTheme = createTheme();

export default function Home() {
    return (
        <ThemeProvider theme={defaultTheme}>
        <Container component="main" maxWidth="xs">
          <CssBaseline />
          <Box
            sx={{
              marginTop: 8,
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
            }}
          >

            <Typography component="h1" variant="h5">
              EkoInsights
            </Typography>

          </Box>
        </Container>
      </ThemeProvider>
    )
}