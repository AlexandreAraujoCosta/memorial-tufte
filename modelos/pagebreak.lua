-- Converte linhas horizontais (---) em quebras de página no LaTeX
function HorizontalRule()
  return pandoc.RawBlock('latex', '\\newpage')
end

-- Suprime headings de nível 1 (# ...) — redundante com a página de título
function Header(el)
  if el.level == 1 then
    return {}
  end
end

-- Converte divs com classe "quadro" no ambiente LaTeX fullwidth+framed
function Div(el)
  if el.classes:includes('quadro') then
    local begin = pandoc.RawBlock('latex', '\\begin{quadro}')
    local finish = pandoc.RawBlock('latex', '\\end{quadro}')
    return {begin} .. el.content .. {finish}
  end
end

-- Converte imagens (Figure) em \includegraphics sem float
function Figure(el)
  local result = {}
  local caption = ''
  if el.caption and el.caption.long and #el.caption.long > 0 then
    caption = pandoc.write(pandoc.Pandoc(el.caption.long), 'latex'):gsub('%s+$', '')
  end
  for _, block in ipairs(el.content) do
    if block.t == 'Plain' or block.t == 'Para' then
      for _, inline in ipairs(block.content) do
        if inline.t == 'Image' then
          local src = inline.src:gsub('\\', '/')
          local attrs = inline.attributes or {}
          local opts = 'keepaspectratio'
          local w = attrs.width
          local h = attrs.height
          if w then
            local pct = w:match('^(%d+)%%$')
            if pct then w = tostring(tonumber(pct)/100) .. '\\linewidth' end
            opts = opts .. ',width=' .. w
          end
          if h then
            local pct = h:match('^(%d+)%%$')
            if pct then h = tostring(tonumber(pct)/100) .. '\\textheight' end
            opts = opts .. ',height=' .. h
          end
          if not w and not h then opts = opts .. ',width=\\linewidth' end
          if inline.classes:includes('margin') then
            local captionTex = ''
            if caption ~= '' then
              captionTex = '\\caption{' .. caption .. '}'
            end
            local offset = attrs.offset or '0pt'
            table.insert(result, pandoc.RawBlock('latex',
              '\\begin{marginfigure}[' .. offset .. ']\\centering\\includegraphics[' .. opts .. ']{' .. src .. '}' .. captionTex .. '\\end{marginfigure}'))
          else
            table.insert(result, pandoc.RawBlock('latex',
              '\\vspace{0.5\\baselineskip}\\begin{fullwidth}\\centering\\includegraphics[' .. opts .. ']{' .. src .. '}\\end{fullwidth}\\vspace{0.5\\baselineskip}'))
          end
        end
      end
    end
  end
  return result
end

-- Converte notas de rodapé em marginnotes (coluna direita estilo Tufte)
function Note(el)
  local latex = pandoc.write(pandoc.Pandoc(el.content), 'latex')
  latex = latex:gsub('^%s+', ''):gsub('%s+$', '')
  return pandoc.RawInline('latex', '\\marginnote{\\fontsize{11}{12}\\selectfont ' .. latex .. '}')
end
