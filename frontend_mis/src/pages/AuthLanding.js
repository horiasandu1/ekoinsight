import * as React from "react";
import { useLocation, useNavigate } from "react-router-dom";

import Link from "@mui/material/Link";
import Card from "@mui/material/Card";

import CssBaseline from "@mui/material/CssBaseline";
import Typography from "@mui/material/Typography";
import Box from "@mui/material/Box";
import { createTheme, ThemeProvider } from "@mui/material/styles";

import Container from "@mui/material/Container";
import { CardContent } from "@mui/material";
import jwt_decode from 'jwt-decode';

export default function AuthLanding() {
  let location = useLocation();
  const defaultTheme = createTheme();

  let decodedInfo = jwt_decode(JSON.stringify(location.state));
  console.log("decoded info")
  console.log(decodedInfo)

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
          <Card>
            <CardContent>
              <Typography>Welcome {decodedInfo.name}</Typography>
            </CardContent>
          </Card>
        </Box>
      </Container>
    </ThemeProvider>
    // <>
    // <h1>Welcome !</h1>
    // <h1>{location.state}</h1>
    // </>
  );
}
