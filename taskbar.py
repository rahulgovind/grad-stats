import rumps
from scrape import get_dataframe


@rumps.clicked("Quit")
def quit_application(_):
    rumps.quit_application()


class GradApp(rumps.App):
    def __init__(self):
        super(GradApp, self).__init__('Grad Cafe', quit_button=None)
        print("Fetching list")
        self.update_list(None)
        self.timer = rumps.Timer(self.update_list, 600)
        self.timer.start()

    def update_list(self, _):
        df = get_dataframe(1)
        d = df.groupby('School').agg({'School': len, 'Submit_Date': max}).rename(
            columns={'School': 'count'})
        d['School'] = d.index
        d = d.sort_values(by='Submit_Date', ascending=False)
        menuitems = d.apply(lambda x: '{} ({})    {}'.format(x['School'],
                                                             x['count'],
                                                             x['Submit_Date'].strftime("%d %B, %Y")), axis=1).tolist()
        menuitems.append(rumps.MenuItem("Quit", quit_application))
        self.menu.clear()
        self.menu.update(menuitems)


if __name__ == "__main__":
    app = GradApp().run()
