export type ThemeName =
    | 'classic'
    | 'ocean'
    | 'violet'
    | 'forest'
    | 'sunset'
    | 'rose'
    | 'custom'

export type Theme = {
    name: ThemeName
    label: string
    accent: string
}

export const themes: Theme[] = [
    {
        name: 'classic',
        label: 'Classic',
        accent: '#111111',
    },
    {
        name: 'ocean',
        label: 'Ocean',
        accent: '#1687c7',
    },
    {
        name: 'violet',
        label: 'Violet',
        accent: '#7c3aed',
    },
    {
        name: 'forest',
        label: 'Forest',
        accent: '#16803c',
    },
    {
        name: 'sunset',
        label: 'Sunset',
        accent: '#f05a28',
    },
    {
        name: 'rose',
        label: 'Rose',
        accent: '#e54872',
    },
    {
        name: 'custom',
        label: 'Свой цвет',
        accent: '#111111',
    },
]