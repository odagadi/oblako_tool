import Image from 'next/image';
import Link from 'next/link';

export default function Banner() {
  return (
    <div className="w-full bg-black border-b border-zinc-800">
      <div className="container mx-auto px-4 py-4">
        <div className="flex justify-between items-center">
          <Link href="/" className="flex items-center">
            <Image
              src="https://cdn.prod.website-files.com/67236b44c3538ff790b92237/672382c00ff5f820be71d46d_Component%201.png"
              alt="Oblako"
              width={200}
              height={50}
              priority
              className="h-[50px] w-auto"
            />
          </Link>
          
          <a
            href="https://www.getoblako.com/contact"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-lg text-black bg-primary hover:bg-primary-hover transition-colors"
          >
            Contact Us
          </a>
        </div>
      </div>
    </div>
  );
}
