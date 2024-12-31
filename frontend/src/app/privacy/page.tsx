import Container from "@/app/_components/container";
import Header from "@/app/_components/header";
import { PostBody } from "@/app/_components/post-body";
import { PostTitle } from "@/app/_components/post-title";

const privacyPolicyContent = `
<p>Effective Date: December 2024</p>
<p>Welcome to Chasing Memories! Your privacy is important to us, and we are committed to protecting any personal information you share. This Privacy Policy explains how we collect, use, and safeguard your information.</p>
<h2>Information We Collect</h2>
<p>We may collect information when you:</p>
<ul>
  <li>Visit our website (e.g., cookies, IP address, and browsing data).</li>
  <li>Interact with our content or subscribe to our newsletter (e.g., name, email address).</li>
</ul>
<h2>How We Use Your Information</h2>
<p>We use your information to:</p>
<ul>
  <li>Provide and improve our website and services.</li>
  <li>Communicate updates, tips, or promotions.</li>
  <li>Analyze website traffic and user behavior to enhance content.</li>
</ul>
<h2>Third-Party Services</h2>
<p>We may use third-party tools (e.g., Google Analytics, Pinterest API) to improve your experience. These services may collect data based on their own privacy policies.</p>
<h2>Your Choices</h2>
<p>You can:</p>
<ul>
  <li>Opt-out of cookies via your browser settings.</li>
  <li>Unsubscribe from email communications anytime.</li>
</ul>
<h2>Contact Us</h2>
<p>If you have any questions or concerns about this policy, please contact us.</p>
`;

export default function PrivacyPolicy() {
  return (
    <main>
      <Container>
        <Header />
        <article className="prose lg:prose-xl mx-auto my-8">
          <PostTitle>Privacy Policy</PostTitle>
          <PostBody content={privacyPolicyContent} />
        </article>
      </Container>
    </main>
  );
}