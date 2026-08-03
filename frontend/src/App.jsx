import { useApp } from "./store/AppContext.jsx";
import AppShell from "./components/layout/AppShell.jsx";
import DashboardView from "./components/dashboard/DashboardView.jsx";
import MarketView from "./components/market/MarketView.jsx";
import PortfolioView from "./components/portfolio/PortfolioView.jsx";
import AdvisorView from "./components/advisor/AdvisorView.jsx";
import AchievementsView from "./components/gamification/AchievementsView.jsx";
import StoriesArchiveView from "./components/archive/StoriesArchiveView.jsx";
import QuestBookView from "./components/quest/QuestBookView.jsx";
import ReplayView from "./components/replay/ReplayView.jsx";
import LoginView from "./components/auth/LoginView.jsx";

const VIEWS = {
  dashboard: DashboardView,
  market: MarketView,
  portfolio: PortfolioView,
  advisor: AdvisorView,
  achievements: AchievementsView,
  archive: StoriesArchiveView,
  quests: QuestBookView,
  replay: ReplayView,
};

export default function App() {
  const { view, authPlayer, authChecked, t } = useApp();
  if (!authChecked) {
    return (
      <div className="flex h-full items-center justify-center">
        <p className="text-sm text-parch-500">{t("loading.init")}</p>
      </div>
    );
  }
  if (!authPlayer) {
    return <LoginView />;
  }
  const View = VIEWS[view] || DashboardView;
  return (
    <AppShell>
      <View />
    </AppShell>
  );
}
