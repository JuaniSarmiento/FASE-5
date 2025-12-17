/**
 * CodeEditor Component
 * Editor de código simple con syntax highlighting
 */
import React from 'react';
import { Code } from 'lucide-react';

interface CodeEditorProps {
  value: string;
  onChange: (value: string) => void;
  language?: string;
  theme?: string;
  showLineNumbers?: boolean;
  readOnly?: boolean;
}

export const CodeEditor: React.FC<CodeEditorProps> = ({
  value,
  onChange,
  language = 'python',
  theme = 'vs-dark',
  showLineNumbers = true,
  readOnly = false,
}) => {
  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    if (!readOnly) {
      onChange(e.target.value);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Tab') {
      e.preventDefault();
      const target = e.target as HTMLTextAreaElement;
      const start = target.selectionStart;
      const end = target.selectionEnd;
      const newValue = value.substring(0, start) + '    ' + value.substring(end);
      onChange(newValue);
      
      // Mover cursor después del tab
      setTimeout(() => {
        target.selectionStart = target.selectionEnd = start + 4;
      }, 0);
    }
  };

  const lines = value.split('\n');

  return (
    <div className="bg-white rounded-lg shadow border border-gray-200 overflow-hidden">
      {/* Header */}
      <div className="bg-gray-800 text-white px-4 py-2 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Code size={18} />
          <span className="font-semibold">Editor de Código</span>
          <span className="text-xs text-gray-400">({language})</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-400">
            {lines.length} líneas
          </span>
        </div>
      </div>

      {/* Editor */}
      <div className="relative">
        {showLineNumbers && (
          <div className="absolute left-0 top-0 bottom-0 w-12 bg-gray-50 border-r border-gray-200 text-gray-500 text-sm font-mono py-4 text-right pr-2 select-none">
            {lines.map((_, idx) => (
              <div key={idx} className="leading-6">
                {idx + 1}
              </div>
            ))}
          </div>
        )}
        <textarea
          value={value}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          readOnly={readOnly}
          className={`w-full font-mono text-sm p-4 focus:outline-none resize-none ${
            showLineNumbers ? 'pl-16' : ''
          } ${theme === 'vs-dark' ? 'bg-gray-900 text-gray-100' : 'bg-white text-gray-900'}`}
          style={{
            minHeight: '400px',
            lineHeight: '1.5rem',
            tabSize: 4,
          }}
          spellCheck={false}
        />
      </div>

      {/* Footer */}
      <div className="bg-gray-50 border-t border-gray-200 px-4 py-2 text-xs text-gray-600 flex items-center justify-between">
        <span>
          {readOnly ? '🔒 Solo lectura' : '✏️ Editando'}
        </span>
        <span>
          {value.length} caracteres
        </span>
      </div>
    </div>
  );
};
