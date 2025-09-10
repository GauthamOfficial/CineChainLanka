import React, { useState, useRef, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { useTranslation } from 'react-i18next';
import { ChevronDownIcon, GlobeAltIcon } from '@heroicons/react/24/outline';

interface LanguageSwitcherProps {
  onLanguageChange?: () => void;
}

const LanguageSwitcher: React.FC<LanguageSwitcherProps> = ({ onLanguageChange }) => {
  const { i18n } = useTranslation();
  const [isOpen, setIsOpen] = useState(false);
  const [dropdownPosition, setDropdownPosition] = useState<'bottom' | 'top'>('bottom');
  const [dropdownStyle, setDropdownStyle] = useState<React.CSSProperties>({});
  const buttonRef = useRef<HTMLButtonElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const languages = [
    { code: 'en', name: 'English', flag: '🇺🇸', shortName: 'EN' },
    { code: 'si', name: 'සිංහල', flag: '🇱🇰', shortName: 'සිං' },
    { code: 'ta', name: 'தமிழ்', flag: '🇱🇰', shortName: 'தமிழ்' }
  ];

  const currentLanguage = languages.find(lang => lang.code === i18n.language) || languages[0];

  const handleLanguageChange = (languageCode: string) => {
    i18n.changeLanguage(languageCode);
    setIsOpen(false);
    onLanguageChange?.();
  };

  const calculatePosition = () => {
    if (!buttonRef.current) return;
    
    const buttonRect = buttonRef.current.getBoundingClientRect();
    const viewportHeight = window.innerHeight;
    const viewportWidth = window.innerWidth;
    const dropdownHeight = 180;
    const dropdownWidth = 208; // w-52 = 208px
    const padding = 10;
    
    // Calculate available space
    const spaceBelow = viewportHeight - buttonRect.bottom - padding;
    const spaceAbove = buttonRect.top - padding;
    
    // Determine position
    let position: 'top' | 'bottom' = 'bottom';
    if (spaceBelow < dropdownHeight && spaceAbove >= dropdownHeight) {
      position = 'top';
    } else if (spaceBelow >= dropdownHeight) {
      position = 'bottom';
    } else {
      position = 'top'; // Default to top if neither space is sufficient
    }
    
    // Calculate horizontal position (right-aligned)
    const left = Math.max(padding, Math.min(buttonRect.right - dropdownWidth, viewportWidth - dropdownWidth - padding));
    
    // Calculate vertical position
    const top = position === 'top' 
      ? buttonRect.top - dropdownHeight - padding
      : buttonRect.bottom + padding;
    
    setDropdownPosition(position);
    setDropdownStyle({
      position: 'fixed',
      top: `${top}px`,
      left: `${left}px`,
      zIndex: 9999,
      maxHeight: '200px',
      overflowY: 'auto'
    });
  };

  const handleToggle = () => {
    if (!isOpen) {
      calculatePosition();
    }
    setIsOpen(!isOpen);
  };

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node) &&
          buttonRef.current && !buttonRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  return (
    <div className="relative">
      <button
        ref={buttonRef}
        onClick={handleToggle}
        className="flex items-center space-x-2 px-3 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors min-w-[100px]"
        title={`Current language: ${currentLanguage.name}`}
      >
        <GlobeAltIcon className="h-4 w-4 flex-shrink-0" />
        <span className="text-lg leading-none">{currentLanguage.flag}</span>
        <span className="truncate max-w-[70px] hidden sm:inline">{currentLanguage.name}</span>
        <span className="truncate max-w-[30px] sm:hidden text-xs">{currentLanguage.shortName}</span>
        <ChevronDownIcon className={`h-3 w-3 flex-shrink-0 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {isOpen && createPortal(
        <div
          ref={dropdownRef}
          className="w-52 bg-white rounded-lg shadow-xl ring-1 ring-black ring-opacity-5 border border-gray-200"
          style={dropdownStyle}
        >
          <div className="py-2">
            {languages.map((language) => (
              <button
                key={language.code}
                onClick={() => handleLanguageChange(language.code)}
                className={`w-full text-left px-4 py-3 text-sm flex items-center space-x-3 hover:bg-gray-50 transition-colors ${
                  i18n.language === language.code ? 'bg-blue-50 text-blue-700 font-medium' : 'text-gray-700'
                }`}
              >
                <span className="text-lg flex-shrink-0">{language.flag}</span>
                <span className="flex-1">{language.name}</span>
                {i18n.language === language.code && (
                  <span className="ml-auto text-blue-600 font-bold">✓</span>
                )}
              </button>
            ))}
          </div>
        </div>,
        document.body
      )}
    </div>
  );
};

export default LanguageSwitcher;
