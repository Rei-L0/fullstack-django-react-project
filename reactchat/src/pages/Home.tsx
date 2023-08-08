import { Box, CssBaseline } from "@mui/material";
import PrimaryAppBar from "./templates/PrimaryAppBar";
import PrimaryDraw from "./templates/PrimaryDraw";
import SecondaryDraw from "./templates/SecondaryDraw";
import Main from "./templates/Main";
import PopularChannels from "../components/PrimaryDraw/PopularChannels";

const Home = () => {
    return (
        <Box
            sx={{
                display: "flex",
            }}
        >
            <CssBaseline />
            <PrimaryAppBar />
            <PrimaryDraw>
                <PopularChannels open={false} />
            </PrimaryDraw>
            <SecondaryDraw></SecondaryDraw>
            <Main />
        </Box>
    );
};

export default Home;
