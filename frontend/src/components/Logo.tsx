interface Props {
  dark?: boolean
  size?: 'sm' | 'md' | 'lg'
}

export default function Logo({ dark = false, size = 'md' }: Props) {
  const textSizes = {
    sm: 'text-base',
    md: 'text-xl',
    lg: 'text-2xl',
  }

  const iconSizes = {
    sm: 'w-6 h-6',
    md: 'w-8 h-8',
    lg: 'w-10 h-10',
  }

  return (
    <div className={`flex items-center gap-2.5 font-bold tracking-tight select-none ${textSizes[size]}`}>
      {/* SAMAAN Concentric Target Symbol Icon */}
      <div className={`relative flex items-center justify-center ${iconSizes[size]}`}>
        <div className="w-full h-full rounded-full border-2 border-teal flex items-center justify-center">
          <div className="w-1/2 h-1/2 rounded-full border border-teal flex items-center justify-center">
            <div className="w-1.5 h-1.5 rounded-full bg-teal" />
          </div>
        </div>
      </div>

      <span className={dark ? 'text-white' : 'text-navy'}>
        SAMAAN <span className="text-teal font-extrabold">AI</span>
      </span>
    </div>
  )
}
