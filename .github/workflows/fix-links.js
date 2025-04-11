import fs from 'fs';
import { glob } from 'glob';
import { load } from 'cheerio';

function fixLink(link) {
    if (!link) return link;
    try {
        return link.trim()
            .replace(/\/+$/, '')
            .replace(/([^:])\/\//g, '$1/')
            .replace(/^(?!(?:http|\/|\.\/))/i, './');
    } catch (err) {
        console.warn(`warning: could not fix link "${link}": ${err.message}`);
        return link;
    }
}

function processFile(filePath) {
    try {
        const content = fs.readFileSync(filePath, 'utf8');
        const lineEnding = content.includes('\r\n') ? '\r\n' : '\n';
        const doctypeMatch = content.match(/<!DOCTYPE[^>]*>/i);
        const originalDoctype = doctypeMatch?.[0];
        
        const comments = [];
        const commentRegex = /<!--[\s\S]*?-->/g;
        let match;
        
        while ((match = commentRegex.exec(content)) !== null) {
            const text = match[0];
            if (text.includes('.')) {
                comments.push({ text, placeholder: `__COMMENT_${comments.length}_` });
            }
        }
        
        const $ = load(content, { decodeEntities: false });
        let modified = false;
        
        const processAttribute = (selector, attr) => {
            $(selector).each((_, elem) => {
                try {
                    const value = $(elem).attr(attr);
                    const fixedValue = fixLink(value);
                    if (value !== fixedValue) {
                        $(elem).attr(attr, fixedValue);
                        modified = true;
                    }
                } catch (err) {
                    console.warn(`warning: could not process ${attr} in ${filePath}: ${err.message}`);
                }
            });
        };
        
        ['a[href]', 'img[src]', 'script[src]', 'link[href]'].forEach(selector => 
            processAttribute(selector, selector.match(/\[(.*?)\]/)[1])
        );
        
        if (modified) {
            let html = $.html({ decodeEntities: false });
            
            if (originalDoctype) {
                html = html.replace(/<!doctype[^>]*>/i, originalDoctype);
            }
            
            comments.forEach(({ text, placeholder }) => {
                html = html.replace(text, placeholder).replace(placeholder, text);
            });
            
            html = html.replace(/\r?\n/g, lineEnding);
            fs.writeFileSync(filePath, html);
            console.log(`fixed links in: ${filePath}`);
        }
    } catch (err) {
        console.error(`error processing file ${filePath}: ${err.message}`);
    }
}

async function main() {
    try {
        const files = await glob(['index.html', 'chapters/**/*.html']);
        
        if (files.length === 0) {
            console.warn('warning: no html files found to process');
            return;
        }

        console.log(`found ${files.length} html files to process`);
        files.forEach(processFile);
        console.log('link fixing process completed!');
    } catch (err) {
        console.error('error finding html files:', err);
        process.exit(1);
    }
}

main(); 
