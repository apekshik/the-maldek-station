#include "StationOpeningComponent.h"
#include "UI/StationOpeningWidget.h"
#include "Components/AudioComponent.h"

void UStationOpeningComponent::SkipForTesting()
{
#if !UE_BUILD_SHIPPING
 bEnableOpening=false;ReleaseInput();
 if(Widget){Widget->RemoveFromParent();Widget=nullptr;}
 if(Atmosphere)Atmosphere->FadeOut(.2f,0.f);
 Elapsed=FMath::Max(Elapsed,20.f);
#endif
}
