import React, { useEffect, useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';
import Navbar from 'components/Navbar.jsx';
import { useAuth } from 'context/authContext.jsx';

// Add these styles to your CSS file
const styles = document.createElement('style');
styles.textContent = `
  html {
    scroll-behavior: smooth;
  }

  @supports (-webkit-overflow-scrolling: touch) {
    html {
      scroll-behavior: auto;
    }
  }

  .section-nav {
    transition: all 0.3s ease;
    opacity: 0.7;
  }

  .section-nav:hover {
    opacity: 1;
  }

  .nav-dot {
    transition: all 0.3s ease;
    transform: scale(1);
  }

  .nav-dot.active {
    transform: scale(1.5);
    background-color: #234869;
  }

  .skip-link {
    position: absolute;
    top: -40px;
    left: 0;
    background: #234869;
    color: white;
    padding: 8px;
    z-index: 100;
    transition: top 0.3s ease;
  }

  .skip-link:focus {
    top: 0;
  }
`;
document.head.appendChild(styles);

const sections = [
  { id: "hero", label: "Home", ariaLabel: "Hero section" },
  { id: "features", label: "Features", ariaLabel: "Features section" },
  { id: "demo", label: "Demo", ariaLabel: "Demo section" },
  { id: "faq", label: "FAQ", ariaLabel: "FAQ section" },
  { id: "contact", label: "Contact", ariaLabel: "Contact section" },
  { id: "cta", label: "Get Started", ariaLabel: "Call to action section" }
];

const SectionNavigation = ({ activeSection }) => (
  <nav
    className="hidden lg:block fixed right-4 top-1/2 transform -translate-y-1/2 z-50 section-nav"
    aria-label="Section navigation"
  >
    <ul className="space-y-4">
      {sections.map((section) => (
        <li key={section.id}>
          <a
            href={`#${section.id}`}
            className="block p-2 text-[#234869] hover:text-[#3a566f] transition-colors"
            aria-label={`Jump to ${section.label} section`}
            aria-current={activeSection === section.id ? "true" : undefined}
          >
            <span className="sr-only">{section.label}</span>
            <div
              className={`w-3 h-3 rounded-full border-2 border-current nav-dot ${
                activeSection === section.id ? 'active' : ''
              }`}
            />
          </a>
        </li>
      ))}
    </ul>
  </nav>
);

const BreadcrumbNavigation = ({ currentSection }) => (
  <nav
    aria-label="Breadcrumb"
    className="py-2 px-4"
  >
    <ol
      className="flex space-x-2 text-sm max-w-7xl mx-auto"
      itemScope
      itemType="https://schema.org/BreadcrumbList"
    >
      <li
        itemProp="itemListElement"
        itemScope
        itemType="https://schema.org/ListItem"
        className="flex items-center"
      >
        <a
          href="/"
          itemProp="item"
          className="text-[#234869] hover:text-[#3a566f]"
        >

        </a>
        <meta itemProp="position" content="1" />
      </li>
      {currentSection && (
        <>
          <li className="flex items-center">
          </li>
          <li
            itemProp="itemListElement"
            itemScope
            itemType="https://schema.org/ListItem"
            className="flex items-center"
          >

            <meta itemProp="position" content="2" />
          </li>
        </>
      )}
    </ol>
  </nav>
);

const SkipLinks = () => (
  <div className="skip-links">
    {sections.map((section) => (
      <a
        key={section.id}
        href={`#${section.id}`}
        className="skip-link"
      >
        Skip to {section.label}
      </a>
    ))}
  </div>
);
const AristtoLandingPage = () => {
  const navigate = useNavigate();
  const [openIndex, setOpenIndex] = useState(null);
  const [activeSection, setActiveSection] = useState('hero');
  const { isAuthenticated, user, loading } = useAuth();
  const sectionRefs = useRef({});

  useEffect(() => {
    if (!loading && isAuthenticated && user?.plan === 'pro') {
      navigate('/');
    }
  }, [isAuthenticated, user, navigate, loading]);

  useEffect(() => {
    // Initialize refs for each section
    sections.forEach(section => {
      sectionRefs.current[section.id] = React.createRef();
    });

    // Set up intersection observer
    const observerOptions = {
      root: null,
      rootMargin: '0px',
      threshold: 0.5,
    };

    const observerCallback = (entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          setActiveSection(entry.target.id);
        }
      });
    };

    const observer = new IntersectionObserver(observerCallback, observerOptions);

    // Observe all sections
    sections.forEach(section => {
      const element = document.getElementById(section.id);
      if (element) observer.observe(element);
    });

    return () => observer.disconnect();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#B39984]"></div>
      </div>
    );
  }

  const toggleAnswer = (index) => {
    setOpenIndex((prevIndex) => (prevIndex === index ? null : index));
  };

  const pageStructuredData = {
    "@context": "https://schema.org",
    "@type": "WebPage",
    "name": "Aristto - AI-Powered Research Assistant",
    "description": "Transform your research workflow with Aristto",
    "url": "https://aristto.com",
    "mainEntity": {
      "@type": "ItemList",
      "itemListElement": sections.map((section, index) => ({
        "@type": "ListItem",
        "position": index + 1,
        "name": section.label,
        "url": `https://aristto.com/#${section.id}`
      }))
    }
  };

  return (
    <>
      <Helmet>
        <title>Aristto - AI-Powered Research Assistant for Scientific Knowledge</title>
        <meta name="title" content="Aristto - AI-Powered Research Assistant for Scientific Knowledge" />
        <meta name="description"
              content="Transform your research workflow with Aristto. Get comprehensive literature reviews, analyze papers, and organize scientific knowledge efficiently with AI assistance." />
        <meta property="og:type" content="website" />
        <meta property="og:url" content="https://aristto.com/" />
        <meta property="og:title" content="Aristto - AI-Powered Research Assistant" />
        <meta property="og:description"
              content="Transform your research workflow with Aristto. Get comprehensive literature reviews, analyze papers, and organize scientific knowledge efficiently." />
        <meta property="og:image" content="https://aristto.com/og-image.png" />
        <meta property="twitter:card" content="summary_large_image" />
        <meta property="twitter:url" content="https://aristto.com/" />
        <meta property="twitter:title" content="Aristto - AI-Powered Research Assistant" />
        <meta property="twitter:description"
              content="Transform your research workflow with Aristto. Get comprehensive literature reviews, analyze papers, and organize scientific knowledge efficiently." />
        <meta property="twitter:image" content="https://aristto.com/twitter-image.png" />
        <meta name="keywords"
              content="research assistant, AI research, literature review, scientific papers, research workflow, academic research, paper analysis" />
        <link rel="canonical" href="https://aristto.com/" />
        <script type="application/ld+json">
          {JSON.stringify(pageStructuredData)}
        </script>
        <script type="application/ld+json">
          {JSON.stringify(featuresStructuredData)}
        </script>
        <script type="application/ld+json">
          {JSON.stringify(faqStructuredData)}
        </script>
      </Helmet>

      <SkipLinks />
      <main className="min-h-screen text-gray-800 font-sans">

        <header>
          <Navbar />
          <BreadcrumbNavigation currentSection={activeSection} />
        </header>

        {/* Hero Section */}
        <section
          id="hero"
          ref={el => sectionRefs.current.hero = el}
          className="px-4 sm:px-6 lg:px-8 py-12 lg:py-20"
          aria-label="Hero"
        >
          <div className="max-w-7xl mx-auto">
            <div className="flex flex-col lg:flex-row items-center gap-8">
              <div className="w-full lg:w-1/2 text-center lg:text-left">
                <h1 className="text-3xl md:text-4xl lg:text-5xl mb-6 lg:mb-8 font-['Iowan_Old_Style'] text-[#234869]">
                  Transforming The Way Researchers Find, Analyze, And Organize Scientific Knowledge
                </h1>
                <button
                  onClick={() => navigate('/signup')}
                  className="px-6 py-3 md:px-8 md:py-4 lg:px-12 lg:py-6 bg-[#234869] text-white text-lg md:text-xl lg:text-2xl font-bold rounded-lg hover:bg-[#3a566f] transition-colors"
                  aria-label="Get started with Aristto"
                >
                  Let&#39;s get started →
                </button>
              </div>

              <div className="w-full lg:w-1/2 hover:scale-110 transition-transform duration-300">
                <img
                  src={'./lit_review.png'}
                  alt="Aristto platform interface showing literature review features"
                  className="w-full h-auto rounded-lg shadow-lg"
                  loading="eager"
                  width="600"
                  height="400"
                />
              </div>
            </div>
          </div>
        </section>

        {/* Features Section */}
        {/* Features Section */}
        <section
          id="features"
          ref={el => sectionRefs.current.features = el}
          className="py-12 lg:py-20 px-4 sm:px-6 lg:px-8"
          aria-label="Features"
          role="region"
          itemScope
          itemType="http://schema.org/ItemList"
        >
          <div className="max-w-7xl mx-auto">
            <h2
              className="text-3xl md:text-4xl font-bold text-center mb-32 font-['Iowan_Old_Style']"
              itemProp="name"
            >
              What can Aristto do for you?
            </h2>

            {/* Desktop circular view - hidden on mobile */}
            <div className="relative max-w-5xl mx-auto h-[700px] hidden lg:block">
              {/* Darker brown faded background circle */}
              <div
                className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] rounded-full"
                style={{
                  background: 'radial-gradient(circle, rgba(179,153,132,0.5) 0%, rgba(179,153,132,0) 70%)'
                }}
                aria-hidden="true"
              ></div>

              {/* Features arranged in a circle */}
              <div itemScope itemType="http://schema.org/ItemList">
                {features.map((feature, index) => {
                  const angle = (index * 360) / features.length
                  const radius = 300
                  const x = Math.cos((angle - 90) * (Math.PI / 180)) * radius
                  const y = Math.sin((angle - 90) * (Math.PI / 180)) * radius

                  return (
                    <div
                      key={feature.title}
                      className="absolute w-52 transform -translate-x-1/2 -translate-y-1/2 flex flex-col items-center text-center transition-all duration-300 hover:scale-110"
                      style={{
                        left: `calc(50% + ${x}px)`,
                        top: `calc(50% + ${y}px)`
                      }}
                      itemScope
                      itemType="http://schema.org/Thing"
                      itemProp="itemListElement"
                    >
                      <div
                        className="mb-4 bg-white rounded-full p-3 shadow-md"
                        role="img"
                        aria-label={feature.alt}
                      >
                        <img
                          src={feature.icon}
                          alt={feature.alt}
                          className="w-12 h-12"
                          loading="lazy"
                          width="48"
                          height="48"
                          itemProp="image"
                        />
                      </div>
                      <h3
                        className="text-xl font-bold mb-2 text-black font-['Iowan_Old_Style']"
                        itemProp="name"
                      >
                        {feature.title}
                      </h3>
                      <p
                        className="text-lg text-black font-['Iowan_Old_Style']"
                        itemProp="description"
                      >
                        {feature.description}
                      </p>
                    </div>
                  )
                })}
              </div>
            </div>

            {/* Mobile view - shown only on mobile */}
            <div
              className="lg:hidden space-y-8"
              itemScope
              itemType="http://schema.org/ItemList"
            >
              {features.map((feature, index) => (
                <div
                  key={feature.title}
                  className="flex flex-col items-center text-center px-4"
                  itemScope
                  itemType="http://schema.org/Thing"
                  itemProp="itemListElement"
                >
                  <div
                    className="mb-4 bg-white rounded-full p-3 shadow-md"
                    role="img"
                    aria-label={feature.alt}
                  >
                    <img
                      src={feature.icon}
                      alt={feature.alt}
                      className="w-12 h-12"
                      loading="lazy"
                      width="48"
                      height="48"
                      itemProp="image"
                    />
                  </div>
                  <h3
                    className="text-xl font-bold mb-2 text-black font-['Iowan_Old_Style']"
                    itemProp="name"
                  >
                    {feature.title}
                  </h3>
                  <p
                    className="text-lg text-black font-['Iowan_Old_Style']"
                    itemProp="description"
                  >
                    {feature.description}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Demo Section */}
        <section
          id="demo"
          ref={el => sectionRefs.current.demo = el}
          className="py-12 lg:py-20 px-4 sm:px-6 lg:px-8"
          aria-label="Demo"
        >
          <div className="max-w-7xl mx-auto text-center">
            <h2 className="text-3xl md:text-4xl font-bold mb-4 font-['Iowan_Old_Style']">
              See Aristto in Action
            </h2>
            <p className="text-lg md:text-xl mb-8 font-['Iowan_Old_Style']">
              Watch our demo video to learn how Aristto can transform your research experience.
            </p>
            <div
              className="max-w-4xl mx-auto aspect-video rounded-lg overflow-hidden shadow-xl bg-white/50 backdrop-blur-sm"
            >
              <iframe
                className="w-full h-full"
                src="https://www.youtube.com/embed/qvLGtHHKRJw"
                title="Aristto Demo Video"
                frameBorder="0"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
              ></iframe>
            </div>
          </div>
        </section>

        {/* FAQ Section */}
        <section
          id="faq"
          ref={el => sectionRefs.current.faq = el}
          className="py-12 lg:py-20 px-4 sm:px-6 lg:px-8"
          aria-label="Frequently Asked Questions"
          itemScope
          itemType="https://schema.org/FAQPage"
        >
          <div className="max-w-7xl mx-auto">
            <h2
              className="text-3xl md:text-4xl font-bold text-center mb-8 lg:mb-16 font-['Iowan_Old_Style']"
              itemProp="name"
            >
              Frequently Asked Questions
            </h2>
            <div className="space-y-4">
              {faqList.map((faq, index) => (
                <div
                  key={index}
                  className="p-4 rounded-lg shadow-md hover:shadow-lg transition-shadow duration-300"
                  itemScope
                  itemProp="mainEntity"
                  itemType="https://schema.org/Question"
                >
                  <div
                    className="flex items-center justify-between cursor-pointer"
                    onClick={() => toggleAnswer(index)}
                    onKeyPress={(e) => {
                      if (e.key === 'Enter' || e.key === ' ') {
                        toggleAnswer(index)
                      }
                    }}
                    role="button"
                    aria-expanded={openIndex === index}
                    tabIndex={0}
                  >
                    <h3
                      className="text-lg md:text-xl text-[#234869] font-bold font-['Iowan_Old_Style'] pr-4"
                      itemProp="name"
                    >
                      {faq.question}
                    </h3>
                    <span
                      className="text-2xl font-bold text-[#234869] flex-shrink-0 transition-transform duration-300"
                      aria-hidden="true"
                      style={{
                        transform: openIndex === index ? 'rotate(45deg)' : 'rotate(0deg)'
                      }}
                    >
                      +
                    </span>
                  </div>
                  {openIndex === index && (
                    <div
                      itemScope
                      itemProp="acceptedAnswer"
                      itemType="https://schema.org/Answer"
                      className="mt-4 transition-all duration-300"
                    >
                      <p
                        className="text-base md:text-lg font-['Iowan_Old_Style']"
                        itemProp="text"
                      >
                        {faq.answer}
                      </p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </section>
        {/* Call-to-Action Section */}
        <section
          id="cta"
          ref={el => sectionRefs.current.cta = el}
          className="py-12 lg:py-20 px-4 sm:px-6 lg:px-8"
          aria-label="Call to Action"
        >
          <div className="max-w-7xl mx-auto text-center text-black p-8 lg:p-12 rounded-lg">
            <h2 className="text-3xl md:text-4xl font-bold mb-8 lg:mb-16 font-['Iowan_Old_Style']">
              Ready to Revolutionize Your Research?
            </h2>
            <button
              onClick={() => navigate('/signup')}
              className="px-6 py-3 md:px-8 md:py-4 lg:px-12 lg:py-6 bg-[#234869] text-white text-lg md:text-xl lg:text-2xl font-bold rounded-lg hover:bg-[#3a566f] transition-colors transform hover:scale-105 duration-300"
              aria-label="Sign up for Aristto"
            >
              Sign Up Now
            </button>
          </div>
        </section>

        {/* Contact Section */}
        <section
          id="contact"
          ref={el => (sectionRefs.current.contact = el)}
          className="py-16"
          aria-label="Contact"
        >
          <div className="max-w-3xl mx-auto px-4 text-center">
            <h2 className="text-2xl font-bold mb-4 font-['Iowan_Old_Style']">
              Contact Us
            </h2>

            <div className="flex justify-center space-x-4">
              <a
                href="mailto:monaal@aristto.com"
                className="px-4 py-2 text-black rounded-lg hover:bg-[#3a566f] transition-colors flex items-center transform hover:scale-110 duration-300"
                aria-label="Email us"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 24 24"
                  fill="#234869"
                  className="w-8 h-8"
                  aria-hidden="true"
                >
                  <path d="M1.5 8.67v8.58a3 3 0 003 3h15a3 3 0 003-3V8.67l-8.928 5.493a3 3 0 01-3.144 0L1.5 8.67z" />
                  <path
                    d="M22.5 6.908V6.75a3 3 0 00-3-3h-15a3 3 0 00-3 3v.158l9.714 5.978a1.5 1.5 0 001.572 0L22.5 6.908z" />
                </svg>
              </a>

              <a
                href="https://www.linkedin.com/company/aristto/"
                target="_blank"
                rel="noopener noreferrer"
                className="px-4 py-2 text-black rounded-lg hover:bg-[#084d93] transition-colors flex items-center transform hover:scale-110 duration-300"
                aria-label="Visit our LinkedIn page"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 24 24"
                  fill="#234869"
                  className="w-8 h-8"
                  aria-hidden="true"
                >
                  <path
                    d="M20.5 2h-17A1.5 1.5 0 002 3.5v17A1.5 1.5 0 003.5 22h17a1.5 1.5 0 001.5-1.5v-17A1.5 1.5 0 0020.5 2zM8 19H5v-9h3zM6.5 8.25A1.75 1.75 0 118.3 6.5a1.78 1.78 0 01-1.8 1.75zM19 19h-3v-4.74c0-1.42-.6-1.93-1.38-1.93A1.74 1.74 0 0013 14.19a.66.66 0 000 .14V19h-3v-9h2.9v1.3a3.11 3.11 0 012.7-1.4c1.55 0 3.36.86 3.36 3.66z" />
                </svg>
              </a>
              <a
                href="https://x.com/AristtoInc"
                target="_blank"
                rel="noopener noreferrer"
                className="px-4 py-2 text-black rounded-lg hover:bg-[#084d93] transition-colors flex items-center transform hover:scale-110 duration-300"
                aria-label="Visit our Twitter page"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 24 24"
                  fill="#234869"
                  className="w-8 h-8"
                  aria-hidden="true"
                >
                  <path
                    d="M24 4.557a9.828 9.828 0 01-2.828.775 4.927 4.927 0 002.165-2.724 9.865 9.865 0 01-3.127 1.195 4.917 4.917 0 00-8.384 4.482 13.945 13.945 0 01-10.11-5.134 4.917 4.917 0 001.523 6.573 4.902 4.902 0 01-2.23-.616v.06a4.919 4.919 0 003.946 4.827 4.903 4.903 0 01-2.224.084 4.918 4.918 0 004.604 3.417A9.867 9.867 0 010 19.539a13.945 13.945 0 007.548 2.212c9.142 0 14.307-7.721 13.995-14.646A10.06 10.06 0 0024 4.557z" />
                </svg>
              </a>
            </div>
          </div>
        </section>


        {/* Footer Section */}
        <footer className="py-8 px-4 sm:px-6 lg:px-8 text-gray-800 bg-gray-50">
          <div className="max-w-7xl mx-auto text-center">
            <p>&copy; {new Date().getFullYear()} Aristto, Inc. All rights reserved.</p>
            <div className="mt-4 text-sm text-gray-600">
              <a href="/privacy" className="hover:text-[#234869] mx-2">Privacy Policy</a>
              <span>|</span>
              <a href="/terms" className="hover:text-[#234869] mx-2">Terms of Service</a>
            </div>
          </div>
        </footer>
      </main>
    </>
  );
};

const features = [
  {
    '@type': 'Thing',
    'position': 1,
    title: 'Get Precise Answers Fast',
    description: 'Ask any research question and get accurate, evidence-based answers',
    icon: '/search.png',
    alt: 'Precise Answers Icon',
    keywords: ['research answers', 'evidence-based answers', 'quick research', 'academic questions'],
    category: 'Research Tools',
    identifier: 'feature-precise-answers'
  },
  {
    '@type': 'Thing',
    'position': 2,
    title: 'Generate Literature Reviews',
    description: 'Get comprehensive, citation-rich literature reviews in minutes',
    icon: '/book.png',
    alt: 'Literature Reviews Icon',
    keywords: ['literature review', 'research review', 'academic citations', 'research synthesis'],
    category: 'Research Tools',
    identifier: 'feature-literature-reviews'
  },
  {
    '@type': 'Thing',
    'position': 3,
    title: 'Chat with Research Papers',
    description: 'Interact with scientific papers to uncover insights tailored to your needs',
    icon: '/chat.png',
    alt: 'Chat with Papers Icon',
    keywords: ['research interaction', 'paper analysis', 'scientific insights', 'research chat'],
    category: 'Research Tools',
    identifier: 'feature-paper-chat'
  },
  {
    '@type': 'Thing',
    'position': 4,
    title: 'Smart Filtering for Relevant Results',
    description: 'Find the right papers by author, rank, year, or citations effortlessly',
    icon: '/setting.png',
    alt: 'Smart Filtering Icon',
    keywords: ['research filtering', 'paper search', 'citation ranking', 'author search'],
    category: 'Research Tools',
    identifier: 'feature-smart-filtering'
  },
  {
    '@type': 'Thing',
    'position': 5,
    title: 'Your Personal Research Library',
    description: 'Save, organize, and revisit your research papers and reviews easily',
    icon: '/book-library.png',
    alt: 'Research Library Icon',
    keywords: ['research organization', 'paper management', 'research library', 'document storage'],
    category: 'Research Tools',
    identifier: 'feature-research-library'
  }
]

const faqList = [
  {
    '@type': 'Question',
    'position': 1,
    question: 'What is Aristto?',
    answer: 'Aristto is a platform designed to transform the way researchers find, analyze, and organize scientific knowledge, ' +
      'saving time and unlocking insights. You can get comprehensive literature reviews and highly specific answers to ' +
      'your research questions, all with specific citations. You can also choose to get a list of most relevant papers to your research needs.',
    keywords: ["Aristto platform", "research assistant", "scientific knowledge", "literature reviews"]
  },
  {
    "@type": "Question",
    "position": 2,
    question: "How much does Aristto cost?",
    answer: "We offer a 7 day free trial so you can get started for free! After the trial, Aristto costs $12.50/month on an annual subscription and $15.00/month on a monthly subscription",
    keywords: ["pricing", "subscription", "free trial", "cost"]
  },
  {
    "@type": "Question",
    "position": 3,
    question: "What types of research areas are supported?",
    answer: "Aristto supports a wide range of disciplines, including life sciences, engineering, social sciences, and more.",
    keywords: ["research areas", "disciplines", "academic fields", "supported subjects"]
  },
  {
    "@type": "Question",
    "position": 4,
    question: "How is Aristto Different from ChatGPT?",
    answer: "Aristto is built specifically for researchers. It can generate comprehensive literature reviews/answer specific questions with inline citations with references to research papers.",
    keywords: ["ChatGPT comparison", "unique features", "citations", "research specific"]
  },
  {
    "@type": "Question",
    "position": 5,
    question: "Is my data secure?",
    answer: "Absolutely. Aristto prioritizes your data's security and privacy, following industry-standard practices to ensure safety.",
    keywords: ["data security", "privacy", "data protection", "security measures"]
  }
];

const featuresStructuredData = {
  "@context": "https://schema.org",
  "@type": "ItemList",
  "name": "Aristto Research Platform Features",
  "description": "Key features of the Aristto AI-powered research assistant platform",
  "numberOfItems": features.length,
  "itemListElement": features.map((feature, index) => ({
    "@type": "ListItem",
    "position": feature.position,
    "item": {
      "@type": "Thing",
      "name": feature.title,
      "description": feature.description,
      "image": feature.icon,
      "identifier": feature.identifier,
      "category": feature.category
    }
  }))
};

const faqStructuredData = {
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": faqList.map(faq => ({
    "@type": "Question",
    "position": faq.position,
    "name": faq.question,
    "acceptedAnswer": {
      "@type": "Answer",
      "text": faq.answer
    }
  }))
}

export default AristtoLandingPage;

