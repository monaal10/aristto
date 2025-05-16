import { useNavigate, useLocation } from "react-router-dom";
import ArrowBackOutlinedIcon from "@mui/icons-material/ArrowBackOutlined";
import { useEffect } from "react";

const BackButton = () => {
  const navigate = useNavigate();
  const handleBack = () => {
    sessionStorage.setItem("previousPageState", JSON.stringify({ scrollY: window.scrollY }));
    navigate(-1);
  };

  useEffect(() => {
    const savedState = JSON.parse(sessionStorage.getItem("previousPageState"));
    if (savedState?.scrollY) {
      window.scrollTo(0, savedState.scrollY);
    }
  }, []); // Restore when the page changes

  return (
    <button
      onClick={handleBack}
      className="flex items-center gap-2 px-4 py-2 rounded-lg transition-all
                 hover:opacity-90 active:scale-95 m-4"
    >
      <ArrowBackOutlinedIcon className="text-[#B39984]" />
    </button>
  );
};

export default BackButton;
