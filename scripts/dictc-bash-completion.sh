# bash completion for dictc

_dictc()
{
    local cur prev words cword split
    _init_completion -s || return

    case "$prev" in
        -h|--help)
            return
            ;;
        -d)
            COMPREPLY=( $( compgen -W 'qq bing' -- "$cur" ) )
            return
            ;;
        -c)
            COMPREPLY=( $( compgen -W 'qq bing dictcn' -- "$cur" ) )
            return
            ;;
    esac

    $split && return 0

    if [[ "$cur" == -* ]]; then
        COMPREPLY=( $( compgen -W "-h --help -d -c" -- "$cur" ) )
        return
    fi

} &&
complete -F _dictc dictc

