import cn from "classnames";
import Link from "next/link";
import Image from "next/image";

type Props = {
  title: string;
  src: string;
  slug?: string;
};

const CoverImage = ({ title, src, slug }: Props) => {
  const image = (
    <Image
      src={src}
      alt={`Cover Image for ${title}`}
      className={cn("shadow-sm m-auto", {
        "hover:shadow-lg transition-shadow duration-200": slug,
      })}
      width={867} // Adjusted width for 2:3 aspect ratio
      height={1300} // Adjusted height for 2:3 aspect ratio
    />
  );
  return (
    <div className="sm:mx-0 max-w-full">
      {slug ? (
        <Link href={`/posts/${slug}`} aria-label={title}>
          {image}
        </Link>
      ) : (
        image
      )}
    </div>
  );
};

export default CoverImage;
