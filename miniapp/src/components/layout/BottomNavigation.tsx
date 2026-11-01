type Tab =
  | 'home'
  | 'subscription'
  | 'balance'
  | 'support'
  | 'account'
  | 'admin'


function BottomNavigation({
  activeTab,
  onChange,
  showAdmin = false,
}: {
  activeTab: Tab
  onChange: (tab: Tab) => void
  showAdmin?: boolean
}) {

  const items: {
    id: Tab
    icon: string
    label: string
  }[] = [

    {
      id: 'home',
      icon: '⌂',
      label: 'Главная',
    },

    {
      id: 'subscription',
      icon: '▣',
      label: 'Подписка',
    },

    {
      id: 'balance',
      icon: '▤',
      label: 'Баланс',
    },

    {
      id: 'support',
      icon: '◯',
      label: 'Поддержка',
    },

  ]


  if (showAdmin) {

    items.push({
      id: 'admin',
      icon: '⚙',
      label: 'Админ',
    })
  }


  return (

    <nav className="bottom-navigation">

      {items.map((item) => (

        <button
          key={item.id}
          className={
            activeTab === item.id
              ? 'nav-item active'
              : 'nav-item'
          }
          onClick={() =>
            onChange(item.id)
          }
        >

          <span className="nav-icon">
            {item.icon}
          </span>

          <span>
            {item.label}
          </span>

        </button>

      ))}

    </nav>
  )
}


export default BottomNavigation
