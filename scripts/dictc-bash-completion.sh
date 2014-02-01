# bash completion for dictc

_dictc()
{
    local cur prev words cword split
    _init_completion -s || return

    case "$prev" in
        -h|--help|--nosound|-v|--version)
            return
            ;;
        -d)
            COMPREPLY=( $( compgen -W 'bing stardict' -- "$cur" ) )
            return
            ;;
        -c)
            COMPREPLY=( $( compgen -W 'bing dictcn spellcheck external' -- "$cur" ) )
            return
            ;;
    esac

    $split && return 0

    if [[ "$cur" == -* ]]; then
        COMPREPLY=( $( compgen -W "-h --help -d -c --nosound -v --version" -- "$cur" ) )
        return
    fi

} &&
complete -F _dictc dictc

