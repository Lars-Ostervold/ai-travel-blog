import Container from "@/app/_components/container";
import { EXAMPLE_PATH } from "@/lib/constants";
import { BLOG_TITLE } from "@/lib/constants";

export function Footer() {
  return (
    <footer className="bg-neutral-50 border-t border-neutral-200 dark:bg-slate-800">
      <Container>
        <div className="py-8 flex flex-col lg:flex-row items-center">
            <a href="/" className="text-xl md:text-l font-bold tracking-tighter leading-tight md:pr-8">
              {BLOG_TITLE}
            </a>
            <h4 className="text-right md:text-left text-sm mt-5 md:mt-0 md:ml-auto">
              © {new Date().getFullYear()} {BLOG_TITLE}. All rights reserved.
            </h4>
          </div>
      </Container>
    </footer>
  );
}

export default Footer;
