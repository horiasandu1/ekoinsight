import * as React from "react";
import { useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";

import Avatar from "@mui/material/Avatar";
import Button from "@mui/material/Button";
import CssBaseline from "@mui/material/CssBaseline";
import Link from "@mui/material/Link";
import Box from "@mui/material/Box";
import LockOutlinedIcon from "@mui/icons-material/LockOutlined";
import Typography from "@mui/material/Typography";
import Container from "@mui/material/Container";
import { createTheme, ThemeProvider } from "@mui/material/styles";

import { GoogleLogin, useGoogleLogin, googleLogout, hasGrantedAllScopesGoogle } from "@react-oauth/google";

// TODO: 404 page, error handling

function Copyright(props) {
  return (
    <Typography
      variant="body2"
      color="text.secondary"
      align="center"
      {...props}
    >
      {"Copyright © "}
      <Link color="inherit" href="https://mui.com/">
        EkoInsight
      </Link>{" "}
      {new Date().getFullYear()}
      {"."}
    </Typography>
  );
}

// TODO remove, this demo shouldn't need to reset the theme.

const defaultTheme = createTheme();

export default function SignIn() {
  const navigate = useNavigate();

  const handleSuccessLogin = (resp) => {
    setGoogleUser(resp);
    console.log("Login successful !");
    navigate("/landing", {state: JSON.stringify(resp)});
  };

  const handleErrorLogin = (err) => {
    console.log("Login error !" + err);
  };

  function handleLogout() {
    googleLogout();
  }

  const [googleUser, setGoogleUser] = useState([]);
  const [userProfile, setUserProfile] = useState([]);

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
          <Avatar sx={{ m: 1, bgcolor: "primary.main" }}>
            <LockOutlinedIcon />
          </Avatar>
          <Typography component="h1" variant="h5">
            Sign in
          </Typography>
          <br></br>
          <GoogleLogin
            text="continue_with"
            size="large"
            onSuccess={handleSuccessLogin}
            onError={handleErrorLogin}
          />
          <Button onClick={handleLogout}>Logout</Button>

        </Box>
        <Copyright sx={{ mt: 8, mb: 4 }} />
      </Container>
    </ThemeProvider>
  );
}
