import { useAuth } from "@/contexts/AuthContext";
import { AuthForm } from "@/components/AuthForm";
import { ChatInterface } from "@/components/ChatInterface";

const Index = () => {
  const { user } = useAuth();

  if (user) {
    return <ChatInterface />;
  }

  return <AuthForm />;
};

export default Index;
