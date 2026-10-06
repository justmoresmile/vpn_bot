type Tab =
  | 'home'
  | 'subscription'
  | 'balance'
  | 'support'


function BottomNavigation({

  activeTab,

  onChange,

}: {

  activeTab: Tab

  onChange: (tab: Tab) => void

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
