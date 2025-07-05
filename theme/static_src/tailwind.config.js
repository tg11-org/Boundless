// Copyright (C) 2025 TG11
// 
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License as
// published by the Free Software Foundation, either version 3 of the
// License, or (at your option) any later version.
// 
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Affero General Public License for more details.
// 
// You should have received a copy of the GNU Affero General Public License
// along with this program.  If not, see <https://www.gnu.org/licenses/>.

module.exports = {
    content: [
        '../templates/**/*.html',
        '../../core/templates/**/*.html',
    ],
    theme: {
        extend: {
            colors: {
                base: 'var(--base)',
                surface: 'var(--surface)',
                text: 'var(--text)',
                accent: 'var(--accent)',
                'header-bg': 'var(--header-bg)',
                'footer-bg': 'var(--footer-bg)',
                'nav-bg': 'var(--nav-bg)',
                'nav-text': 'var(--nav-text)',
                'button-bg': 'var(--button-bg)',
                'button-hover': 'var(--button-hover)',
                'input-bg': 'var(--input-bg)',
                'input-text': 'var(--input-text)',
                'input-border': 'var(--input-border)',
                'code-bg': 'var(--code-bg)',
                'code-text': 'var(--code-text)',
                'quote-bg': 'var(--quote-bg)',
                'quote-border': 'var(--quote-border)',
                'link': 'var(--link-color)',
                'link-hover': 'var(--link-hover)',
            },
            borderRadius: {
                DEFAULT: 'var(--radius)',
            },
            boxShadow: {
                DEFAULT: 'var(--shadow)',
            },
            fontFamily: {
                sans: 'var(--font-sans)',
                serif: 'var(--font-serif)',
            },
            fontSize: {
                base: 'var(--font-size-base)',
                lg: 'var(--font-size-lg)',
                sm: 'var(--font-size-sm)',
            }
        }          
    },
    plugins: [],
}